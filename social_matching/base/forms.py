from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


# Modified user creation form to use the updated user class.
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("email", "password1", "password2")


class ModifiedBigFiveInventory(forms.Form):
    choices = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    q1 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, label="Is talkative")
    q2 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, label="Tends to find fault with others")
    q3 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, label="Is emotionally stable, not easily upset")
    q4 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, label="Is depressed, blue")
    q5 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, label="Has an assertive personality")
    q6 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, label="Can be cold and aloof")
    q7 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, label="Is reserved")
    q8 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, label="Is helpful and unselfish with others")
    q9 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, label="Can be moody")
    q10 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Is relaxed, handles stress well")
    q11 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Is sometimes shy, inhibited")
    q12 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Is considerate and kind to almost everyone")
    q13 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Is full of energy")
    q14 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Starts quarrels with others")
    q15 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Remains calm in tense situations")
    q16 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Can be tense")
    q17 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Is outgoing, sociable")
    q18 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Is sometimes rude to others")
    q19 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Generates a lot of enthusiasm")
    q20 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Has a forgiving nature")
    q21 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Gets nervous easily")
    q22 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Worries a lot")
    q23 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Likes to cooperate with others")
    q24 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Tends to be quiet")
    q25 = forms.ChoiceField(choices=choices, widget=forms.RadioSelect,  label="Is generally trusting")
