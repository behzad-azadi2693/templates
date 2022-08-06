from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms

messages = {
    'required':'این فیلد الزامیست',
    'invalid':'مقدار فیلد صحیح نمی باشد',
    'max_length':'مقدار فیلد بیشتر از حد مجاز',
    'min_length':'مقدار فیلد کمتر از حد مجاز',
}

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label='password', widget=forms.PasswordInput)
    password_confierm = forms.CharField(label='password confierm', widget=forms.PasswordInput)

    class Meta:
        models = get_user_model()
        fields = ('phone', 'password', 'password_confierm')

    def clean_password_confierm(self):
        cd = self.cleaned_data
        if cd['password'] and cd['password_confierm'] and cd['password'] != cd['password_confierm']:
            raise forms.ValidationError('Password and password are not the same')

        return cd['password_confierm']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    class Meta:
        models = get_user_model()
        fields = ('phone', 'password')

    def clean_password(self):
        return self.initial['password']