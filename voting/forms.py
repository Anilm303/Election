from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Candidate, CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


class VoteForm(forms.Form):
    candidate = forms.ModelChoiceField(queryset=Candidate.objects.none(), empty_label="Select a candidate")

    def __init__(self, *args, **kwargs):
        election = kwargs.pop("election")
        super().__init__(*args, **kwargs)
        self.fields["candidate"].queryset = election.candidates.all()
