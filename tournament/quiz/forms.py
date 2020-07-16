from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import Category, User

class SignUpForm(UserCreationForm):
    interests = forms.ModelMultipleChoiceField(
    queryset=Category.objects.all(),
    widget=forms.CheckboxSelectMultiple,
    required=True
)
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'interests')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.save()
        user.interests.add(*self.cleaned_data.get('interests'))
        return user
    
