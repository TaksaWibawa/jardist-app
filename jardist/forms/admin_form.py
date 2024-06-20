from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from jardist.models.role_models import Department, Role

class UserAdminForm(UserCreationForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all())
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'department',)