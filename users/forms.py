from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class UserRegistrationForm(forms.ModelForm):

    email = forms.EmailField(max_length=255, help_text="Required. Add a valid email address.")
    username = forms.CharField(max_length=255, help_text="Required. Add a unique Username.")
    password = forms.CharField(widget=forms.PasswordInput(), help_text='Password Required.')

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = User.objects.exclude(pk=self.instance.pk).get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(f'Email {email} is already in use.')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            account = User.objects.exclude(pk=self.instance.pk).get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(f'Username {username} is already in use.')


class UserAuthenticationForm(forms.ModelForm):

    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password')

    # def save(self, request):
    #     email = self.cleaned_data['email']
    #     password = self.cleaned_data['password']
    #     user = authenticate(email=email, password=password)
    #     if user:
    #         login(request, user)

    def clean(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']
            if not authenticate(username=username, password=password):
                raise forms.ValidationError('Invalid Login')
