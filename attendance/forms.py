from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User

class CustomPasswordResetForm(PasswordResetForm):

    def clean_email(self):

        email = self.cleaned_data['email']

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "No account is registered with this email address."
            )

        return email
    
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User


class CustomPasswordResetForm(
    PasswordResetForm
):

    def clean_email(self):

        email = self.cleaned_data['email']

        if not email.endswith('@sonarpurmahavidyalaya.ac.in'):
            raise forms.ValidationError(
                'Use your official college email.'
            )

        if not User.objects.filter(
                email=email).exists():

            raise forms.ValidationError(
                'No account exists with this email.'
            )

        return email
    
from django import forms
from .models import Subject, Semester, Section

COMPONENT_CHOICES = [
    ('Theory', 'Theory'),
    ('Tutorial', 'Tutorial'),
    ('Practical', 'Practical'),
]

class StudentUploadForm(forms.Form):
    excel_file = forms.FileField()

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all()
    )

    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all()
    )

    section = forms.ModelChoiceField(
        queryset=Section.objects.all()
    )

    component = forms.ChoiceField(
        choices=COMPONENT_CHOICES
    )

from django import forms
from .models import TeacherProfile


class TeacherProfileForm(forms.ModelForm):

    class Meta:
        model = TeacherProfile

        fields = [
            'photo',
            'designation',
            'department',
            'phone',
            'email',
            'address',
            'blood_group',
            'joining_date',
        ]