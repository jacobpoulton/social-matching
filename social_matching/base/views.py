from django.contrib.auth import authenticate, login
from django.views.generic.edit import CreateView
from django.shortcuts import render
from django.urls import reverse_lazy
from . import forms


def home(request):
    # Show static welcome page to non-logged in users
    if not request.user.is_authenticated:
        return render(request, 'welcome.html')

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
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Called once valid form data has been submitted
        redirect = super(CreateUserView, self).form_valid(form)
        user = authenticate(self.request,
                            username=form.cleaned_data.get('username'),
                            password=form.cleaned_data.get('password2'))
        login(self.request, user)
        return redirect
