from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from .models import ContactFormData
class UserCreateForm(UserCreationForm):
    """
    A UserCreationForm with optional password inputs.
    """
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        # self.fields['username'].initial = 'Hybrid'
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    def clean_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = super(UserCreationForm, self).clean_password2()
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError("Fill out both fields")
        return password2
 
class ContactForm(ModelForm):
    class Meta:
        model = ContactFormData
        fields = '__all__'