from django.shortcuts import render


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
