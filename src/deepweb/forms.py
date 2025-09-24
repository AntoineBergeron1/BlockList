from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import User



class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        help_text=None,
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text=None,
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text=None,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )
        error_messages = {
            "username": {
                "required": "Nom d'utilisateur : Le nom d'utilisateur est obligatoire.",
                "invalid": "Nom d'utilisateur : Le nom d'utilisateur n'est pas valide.",
            },
            "password1": {
                "required": "Mot de passe : Le mot de passe est obligatoire",
                "invalid": "Mot de passe : Le mot de passe est invalide",
            },
            "email": {
                "invalid": "Courriel : Le courriel est invalide",
                "required": "Courriel : Le courriel est obligatoire",
            },

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            self.fields["password1"].help_text = None
            self.fields["password2"].help_text = None
            self.fields["username"].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Nom d'utilisateur",
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Mot de passe",
    )

