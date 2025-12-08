from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import Select

from .models import IPAddress, Report

User = get_user_model()


class SelectWithDisabledOption(Select):
    """Custom Select widget that allows disabling specific options"""

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        # Disable the empty option (value='')
        if value == "":
            option["attrs"]["disabled"] = "disabled"
        return option


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        help_text=None,
        error_messages={
            "required": "Le courriel est obligatoire",
            "invalid": "Le courriel est invalide",
        },
        label="Courriel : ",
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text=None,
        error_messages={
            "required": "Le prénom est obligatoire",
        },
        label="Prénom : ",
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text=None,
        error_messages={
            "required": "Nom : Le nom est obligatoire",
        },
        label="Nom : ",
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe : ",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Veuillez confirmer votre mot de passe.",
        },
    )
    password1 = forms.CharField(
        label="Mot de passe : ",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Mot de passe obligatoire.",
        },
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

    def clean_email(self):
        email = self.cleaned_data["email"]
        active_user = User.objects.filter(email=email, is_active=True).first()
        if active_user:
            raise forms.ValidationError("Un compte actif avec cet email existe déjà.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "Mot de passe : Les deux mots de passe ne correspondent pas."
            )
        return password2

    def save(self, commit=True):
        email = self.cleaned_data["email"]
        existing_user = User.objects.filter(email=email, is_active=False).first()

        if existing_user:
            existing_user.username = self.cleaned_data["username"]
            existing_user.first_name = self.cleaned_data["first_name"]
            existing_user.last_name = self.cleaned_data["last_name"]
            existing_user.set_password(self.cleaned_data["password1"])
            existing_user.is_active = True
            if commit:
                existing_user.save()
            return existing_user

        user = super().save(commit=False)
        user.email = email
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
        error_messages={
            "required": "Le nom d'utilisateur est obligatoire",
            "invalid": "Le nom d'utilisateur n'est pas conforme",
        },
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Mot de passe",
        error_messages={
            "required": "Le mot de passe est obligatoire",
            "invalid": "Le mot de passe n'est pas conforme",
        },
    )


class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Prénom",
        error_messages={"invalid": "Entrez un prénom valide."},
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Nom de famille",
        error_messages={"invalid": "Entrez un nom valide."},
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        label="Email",
        error_messages={"invalid": "Entrez une adresse email valide."},
        min_length=5,
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Modifier mot de passe",
        error_messages={"invalid": "Entrez un mot de passe valide."},
    )
    password_confirm = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirmer mot de passe",
        error_messages={"invalid": "Entrez un mot de passe valide."},
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
        ]


class ReportForm(forms.ModelForm):
    """
    Form for reporting an IP address.
    IP address field can be readonly when coming from IP detail page.
    """

    ip_address = forms.CharField(
        label="Adresse IP",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "L'adresse IP est obligatoire.",
            "invalid": "L'adresse IP n'est pas valide.",
        },
    )

    class Meta:
        model = Report
        fields = ["ip_address", "reason", "comment"]
        widgets = {
            "reason": SelectWithDisabledOption(attrs={"class": "form-control"}),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Décrivez l'activité suspecte observée...",
                }
            ),
        }
        labels = {
            "reason": "Raison du signalement",
            "comment": "Commentaire (optionnel)",
        }
        error_messages = {
            "reason": {
                "required": "La raison du signalement est obligatoire.",
            },
        }

    def __init__(self, *args, **kwargs):
        ip_address = kwargs.pop("ip_address", None)
        readonly = kwargs.pop("readonly", False)
        super().__init__(*args, **kwargs)

        # Pre-fill IP address if provided
        if ip_address:
            self.fields["ip_address"].initial = ip_address
            self.fields["ip_address"].widget = forms.HiddenInput()
            # Add a readonly display field
            self.fields["ip_display"] = forms.CharField(
                label="Adresse IP",
                initial=ip_address,
                disabled=True,
                required=False,
                widget=forms.TextInput(attrs={"class": "form-control"}),
            )

        # Make IP field readonly if specified
        if readonly:
            self.fields["ip_address"].widget.attrs["readonly"] = True

    def clean_ip_address(self):
        """
        Validate and get or create IP address.
        """
        ip_input = self.cleaned_data.get("ip_address")

        # If ip_input is already an IPAddress instance
        if isinstance(ip_input, IPAddress):
            return ip_input

        # If it's a string, validate and get or create
        if isinstance(ip_input, str):
            try:
                ip_address, created = IPAddress.objects.get_or_create(address=ip_input)
                return ip_address
            except Exception as e:
                raise forms.ValidationError(f"Adresse IP invalide : {e}")

        return ip_input


class SearchForm(forms.Form):
    recherche = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Entrez une adresse IP...",
            }
        ),
    )

    tries = forms.ChoiceField(
        choices=[
            ("default", "Plus récents (Défaut)"),
            ("reputationDesc", "Réputation (pire d'abord)"),
            ("reputationAsc", "Réputation (meilleur d'abord)"),
            ("modificationDesc", "Dernière modification"),
        ],
        label="",
        widget=forms.Select(
            attrs={
                "class": "form-select form-select-lg",
            }
        ),
        required=False,
    )

    filtres = forms.ChoiceField(
        choices=[
            ("", "Tous"),
            ("4", "IPv4"),
            ("6", "IPv6"),
        ],
        label="",
        widget=forms.Select(attrs={"class": "form-select form-select-lg"}),
        required=False,
    )
