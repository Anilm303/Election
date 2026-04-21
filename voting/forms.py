from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Candidate, CustomUser, VoterProfile, OTPVerification

try:
    from captcha.fields import ReCaptchaField
    from captcha.widgets import ReCaptchaV2Checkbox
    CAPTCHA_AVAILABLE = True
except ImportError:
    CAPTCHA_AVAILABLE = False


class LoginForm(forms.Form):
    """Form for user login with username or email"""
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )


class EnhancedRegisterForm(UserCreationForm):
    """Enhanced registration form with email and optional CAPTCHA"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
        
        # Only add CAPTCHA if available
        if CAPTCHA_AVAILABLE:
            self.fields['captcha'] = ReCaptchaField(widget=ReCaptchaV2Checkbox())
        
        # Apply Bootstrap styling to all fields
        for field in self.fields:
            if field != 'captcha':  # CAPTCHA has its own styling
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })


class OTPVerificationForm(forms.Form):
    """Form for OTP verification"""
    otp_code = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'autocomplete': 'off',
            'inputmode': 'numeric',
            'maxlength': '6'
        })
    )

    def clean_otp_code(self):
        otp_code = self.cleaned_data.get('otp_code')
        if otp_code and not otp_code.isdigit():
            raise forms.ValidationError("OTP must contain only digits.")
        return otp_code


class Enable2FAForm(forms.Form):
    """Form to enable 2FA for user"""
    enable_2fa = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class VoterProfileForm(forms.ModelForm):
    """Form for voter profile completion"""
    class Meta:
        model = VoterProfile
        fields = ['unique_voter_id', 'date_of_birth', 'gender', 'address', 'contact_number']
        widgets = {
            'unique_voter_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Citizenship Number or Voter ID'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Residential Address'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
        }


class CandidateForm(forms.ModelForm):
    """Form for managing candidate profiles"""
    class Meta:
        model = Candidate
        fields = ['name', 'email', 'phone', 'party', 'symbol', 'manifesto', 
                 'biography', 'photo', 'position', 'is_independent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Number'
            }),
            'party': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Political Party'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Party Symbol'
            }),
            'manifesto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Electoral Manifesto'
            }),
            'biography': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Biography'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'position': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number'
            }),
            'is_independent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class VoteForm(forms.Form):
    """Enhanced vote form with validation"""
    candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.none(),
        empty_label="Select a candidate",
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, *args, **kwargs):
        election = kwargs.pop("election")
        super().__init__(*args, **kwargs)
        self.fields["candidate"].queryset = election.candidates.all()


class ElectionForm(forms.Form):
    """Form for creating/updating elections"""
    from django.forms import ModelChoiceField
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Election Title'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Description'
        })
    )
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    require_voter_verification = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    publish_results = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError("End time must be after start time.")
        return cleaned_data


class LanguagePreferenceForm(forms.Form):
    """Form to set language preference"""
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ne', 'Nepali'),
    ]
    
    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
