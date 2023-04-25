from django.contrib.auth import authenticate, login
from django.contrib.admin.views import decorators
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.conf import settings
from django.template import loader
import django.core.mail as mail
from . import forms, models
from statistics import variance
import random


def home(request):
    # Show static welcome page to non-logged in users
    if not request.user.is_authenticated:
        return render(request, 'welcome.html')

    # Make users fill in details if haven't
    if not request.user.details:
        return redirect('details')

    # Show main home page to full users
    context = {
        'matches': request.user.match_count(),
        'match_again': request.user.preferences.in_match_pool,
        'email_match': request.user.preferences.notification_match,
        'email_survey': request.user.preferences.notification_survey,
        'contact': request.user.contact,
        'survey_open': True,
    }
    return render(request, 'home.html', context=context)


def about(request):
    return render(request, 'about.html')


def toggle_matching(request):
    # Get POST request
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'message': "Unauthenticated request sender.", 'switch_state': toggle})
        toggle = request.POST.get('switchValue')

        # Toggle preferences
        prefs = request.user.preferences
        prefs.in_match_pool = toggle.lower()[0] == "t"
        prefs.save()

        # Send response
        return JsonResponse({'message': "Matching preference toggled succesfully.", 'switch_state': toggle})
    return redirect('home')


def preferences_update(request):
    # Update user prefs if possible
    if request.POST and request.user.is_authenticated and request.user.preferences:
        request.user.preferences.notification_match = 'notification_match' in request.POST.keys()
        request.user.preferences.notification_survey = 'notification_survey' in request.POST.keys()
        request.user.preferences.save()
        request.user.contact = request.POST.get('contact')
        request.user.save()

    # Redirect to home regardless
    return redirect('home')


class CreateUserView(CreateView):
    form_class = forms.CustomUserCreationForm
    template_name = 'registration/create-user.html'
    success_url = reverse_lazy('details')

    def form_valid(self, form):
        # Get consent
        form.cleaned_data['consent_information_sheet'] = form.data['consent_information_sheet'] == 'on'
        form.cleaned_data['consent_participation'] = form.data['consent_participation'] == 'on'
        form.cleaned_data['consent_publication'] = form.data['consent_publication'] == 'on'

        # Log the new user in
        redirect_url = super().form_valid(form)
        user = authenticate(self.request,
                            username=form.cleaned_data.get('email'),
                            password=form.cleaned_data.get('password2'))
        login(self.request, user)

        print(user.consent_information_sheet, form.data, form.cleaned_data)

        # Add new preferences object to the user
        prefs = models.UserPreferences()
        prefs.in_match_pool = False
        prefs.save()
        user.preferences = prefs
        user.save()

        # Redirect back to page
        return redirect_url


def delete_user(request):
    request.user.delete()
    return redirect('home')


class GiveDetailsView(FormView):
    form_class = forms.ModifiedBigFiveInventory
    template_name = 'details.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['set_before'] = bool(self.request.user.details)
        return context

    def form_valid(self, form):
        # Called once valid form data has been submitted
        redirect_url = super().form_valid(form)

        # Get response values
        agreeableness = (
            6 - int(form.cleaned_data.get('q2')),
            6 - int(form.cleaned_data.get('q6')),
            int(form.cleaned_data.get('q8')),
            int(form.cleaned_data.get('q12')),
            6 - int(form.cleaned_data.get('q14')),
            6 - int(form.cleaned_data.get('q18')),
            int(form.cleaned_data.get('q20')),
            int(form.cleaned_data.get('q23')),
            int(form.cleaned_data.get('q25')),
        )
        neuroticism = (
            6 - int(form.cleaned_data.get('q3')),
            int(form.cleaned_data.get('q4')),
            int(form.cleaned_data.get('q9')),
            6 - int(form.cleaned_data.get('q10')),
            6 - int(form.cleaned_data.get('q15')),
            int(form.cleaned_data.get('q16')),
            int(form.cleaned_data.get('q21')),
            int(form.cleaned_data.get('q22')),
        )
        extroversion = (
            int(form.cleaned_data.get('q1')),
            int(form.cleaned_data.get('q5')),
            6 - int(form.cleaned_data.get('q7')),
            6 - int(form.cleaned_data.get('q11')),
            int(form.cleaned_data.get('q13')),
            int(form.cleaned_data.get('q17')),
            int(form.cleaned_data.get('q19')),
            6 - int(form.cleaned_data.get('q24')),
        )

        # Get details model
        if self.request.user.details:
            details = self.request.user.details
        else:
            details = models.UserDetails()

        # Average values and set details
        # Due to the way the field works, clip value to 0.999
        details.agreeableness = min((sum(agreeableness) / len(agreeableness) - 1) / 4, 0.999)
        details.neuroticism = min((sum(neuroticism) / len(neuroticism) - 1) / 4, 0.999)
        details.extroversion = min((sum(extroversion) / len(extroversion) - 1) / 4, 0.999)
        details.heuristic = min(details.agreeableness * (1 - details.neuroticism), 0.999)
        details.save()

        # Set the details to the user
        self.request.user.details = details
        self.request.user.save()

        # Enter the user into the match pool
        prefs = self.request.user.preferences
        prefs.in_match_pool = True
        prefs.save()

        # Return user
        return redirect_url


class ViewMatches(ListView):
    model = models.Match
    template_name = "matches.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = context['object_list'].filter(details_list=self.request.user.details)
        context['user'] = self.request.user
        return context


@decorators.staff_member_required()
def matching(request):
    message = "Matching Failed."

    # Confirm that matching minimum conditions are met
    if not models.User.can_match():
        message = "Not enough users present to match."
    else:
        # Get users to be matched
        users = models.User.matchable_users()

        # Calculate group size:
        # - Aims to minimise the remainder of users.
        # - Sorts to also try and have the highest number of groups where possible.
        total = len(users)
        group_size = None
        for i in range(settings.GROUP_SIZE_MIN, settings.GROUP_SIZE_MAX + 1):
            if not group_size or (group_size and total % group_size > total % i):
                group_size = i
                # Break if reached best possible option
                if total % i == 0:
                    break

        # Calculate number of groups and remainder
        groups_total = total // group_size
        remainder = total % group_size

        # Create heuristic based rows:
        # - Aims to spread out agreeableness and neuroticism evenly
        users_heuristic = users.order_by('details__heuristic').reverse()
        rows = []
        for i in range(group_size if remainder == 0 else group_size + 1):
            rows.append(users_heuristic[i * groups_total:min((i + 1) * groups_total, total)])

        # Sort the rows based on extroversion
        # - Aims to keep people of the same extroversion level together
        for i in range(len(rows)):
            row = sorted(rows[i], key=lambda model: model.details.extroversion)
            rows[i] = row

        # Slight random shuffle to the rows
        # - Aims to produce different groups each time, for different experiences
        # - Often pairs with people from before, but not exact same groups
        for row in rows:
            for i in range(len(row) - 1):
                if random.getrandbits(1):
                    tmp = row[i]
                    row[i] = row[i + 1]
                    row[i + 1] = tmp

        # Generate groups
        groups = []
        average_extroversions = []
        for i in range(groups_total):
            group = []
            extroversions_sum = 0
            for slot in range(group_size):
                user = rows[slot][i]
                group.append(user)
                extroversions_sum += float(user.details.extroversion)
            groups.append(group)
            average_extroversions.append((i, extroversions_sum / group_size))

        # Add on remainder if necessary
        if remainder > 0:
            average_extroversions_sorted = sorted(average_extroversions, key=lambda pair: pair[1])
            for i in range(remainder):
                groups[average_extroversions_sorted[i][0]].append(rows[group_size][i])

        # Save the new matches to the model
        means = []
        variances = []
        emails = []
        for group in groups:
            # Calculate stats & emails
            values = [[], [], [], []]
            email_recipients = []
            for member in group:
                if member.preferences.notification_match:
                    email_recipients.append(member.email)
                values[0].append(member.details.agreeableness)
                values[1].append(member.details.neuroticism)
                values[2].append(member.details.extroversion)
                values[3].append(member.details.heuristic)
            means.append([
                round(sum(values[0]) / len(group), 3),
                round(sum(values[1]) / len(group), 3),
                round(sum(values[2]) / len(group), 3),
                round(sum(values[3]) / len(group), 3),
            ])
            variances.append([
                round(variance(values[0]), 3),
                round(variance(values[1]), 3),
                round(variance(values[2]), 3),
                round(variance(values[3]), 3),
            ])

            # Send emails
            context = {
                'count': len(group),
                'url': settings.BASE_URL + reverse_lazy('matches'),
            }
            email_text = loader.get_template("email-match.txt").render(context=context)
            email_html = loader.get_template("email-match.html").render(context=context)
            email = mail.EmailMultiAlternatives(
                "New Match - Play Games with New Friends!",
                email_text,
                settings.DEFAULT_FROM_EMAIL,
                email_recipients,
            )
            email.attach_alternative(email_html, "text/html")
            emails.append(email)

            # Don't save to model if in debug mode
            if settings.DEBUG:
                continue

            # Initialse the match
            match = models.Match()
            match.save()

            # Add members and notify them
            for member in group:
                match.details_list.add(member.details)

            match.save()

            # Add metadata
            match.mean_agreeableness = means[-1][0]
            match.mean_neuroticism = means[-1][1]
            match.mean_extroversion = means[-1][2]
            match.mean_heuristic = means[-1][3]
            match.variance_agreeableness = variances[-1][0]
            match.variance_neuroticism = variances[-1][1]
            match.variance_extroversion = variances[-1][2]
            match.variance_heuristic = variances[-1][3]
            match.save()
        connection = mail.get_connection()
        connection.send_messages(emails)

        # Generate success message
        # - Include (anonymised) details on the matching
        message = f"<h2>Success!</h2><p>{groups_total} groups of size {group_size} with a remainder of {remainder}/{total} users.</p>"
        for i in range(groups_total):
            message += f"<h3>Group #{i + 1}.</h3><ul><p>"
            details = ""
            for member in groups[i]:
                message += f"{str(hash(str(member.id)))[:4]}, "  # Anonymises with cryptographic hash
                details += f"<li>A: <code><u>{member.details.agreeableness}</u></code>, N: <code><u>{member.details.neuroticism}</code></u>, E: <code><u>{member.details.extroversion}</code></u></li>"
            message += "</p>" + details
            message += f"<br>Means:<ul><li>A: {means[i][0]}</li><li>N: {means[i][1]}</li><li>E: {means[i][2]}</li><li>H: {means[i][3]}</li></ul>"
            message += f"<br>Variances:<ul><li>A: {variances[i][0]}</li><li>N: {variances[i][1]}</li><li>E: {variances[i][2]}</li><li>H: {variances[i][3]}</li></ul></ul>"

    return render(request, 'matching.html', context={'message': message})
