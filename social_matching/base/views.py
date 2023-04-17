from django.contrib.auth import authenticate, login
from django.views.generic.edit import CreateView, FormView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from . import forms, models


def home(request):
    # Show static welcome page to non-logged in users
    if not request.user.is_authenticated:
        return render(request, 'welcome.html')

    # Make users fill in details if haven't
    if not request.user.details:
        return redirect('details')

    # Show main home page to full users
    context = {  # TODO: Add functionality to contexts
        'match_open': True,
        'matched': True,
        'survey_open': True,
    }
    return render(request, 'home.html', context=context)


class CreateUserView(CreateView):
    form_class = forms.CustomUserCreationForm
    template_name = 'registration/create-user.html'
    success_url = reverse_lazy('details')

    def form_valid(self, form):
        # Called once valid form data has been submitted
        redirect_url = super().form_valid(form)
        user = authenticate(self.request,
                            username=form.cleaned_data.get('email'),
                            password=form.cleaned_data.get('password2'))
        login(self.request, user)
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
        details.agreeableness = (sum(agreeableness) / len(agreeableness) - 1) / 4
        details.neuroticism = (sum(neuroticism) / len(neuroticism) - 1) / 4
        details.extroversion = (sum(extroversion) / len(extroversion) - 1) / 4
        details.save()

        # Set the details to the user
        self.request.user.details = details
        self.request.user.save()

        # Return user
        return redirect_url


def matching(request):
    print(models.User.can_match())
    return redirect('home')
