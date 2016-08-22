# coding:utf-8

from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm

from account.models import UserProfile


class UserForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    mobile = forms.CharField(label="Mobile")

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages[u'duplicate_email'],
            code='duplicate_email',
        )

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"]

        if not UserProfile.objects.filter(mobile=mobile).exists():
            return mobile

        raise forms.ValidationError(
            self.error_messages[u'duplicate_mobile'],
            code='duplicate_mobile',
        )

    def save(self, password=None , commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                mobile=self.cleaned_data['mobile'],
                keystone_password=password)

        return user



class ChangepwdForm(forms.Form):
    oldpassword = forms.CharField(
        required=True,
        label=u"请输入原密码",
        error_messages={'required': u'input'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"",
            }
        ),
    )
    newpassword1 = forms.CharField(
        required=True,
        label=u"请输入新密码",
        error_messages={'required': u'input'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"",
            }
        ),
    )
    newpassword2 = forms.CharField(
        required=True,
        label=u"再输入一次",
        error_messages={'required': u'input again'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"",
            }
        ),
    )
    '''
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"not none")
        elif self.cleaned_data['newpassword1'] <> self.cleaned_data['newpassword2']:
            raise forms.ValidationError(u"error")
        else:
            cleaned_data = super(ChangepwdForm, self).clean()
        return cleaned_data
            '''