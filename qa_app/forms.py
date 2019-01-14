from django import forms
from .models import Question, Answer, User  #, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.safestring import mark_safe
from sorl.thumbnail import get_thumbnail


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']

    def clean_tags(self):
        data = self.cleaned_data['tags']
        if data.count() > settings.MAX_TAGS:
            raise ValidationError('Maximum 3 tags')
        return data


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content', 'question']
        widgets = {'question': forms.HiddenInput, }

    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user', None)
    #     super().__init__(*args, **kwargs)
    #
    # def clean(self):
    #     self.instance.author = self.user
    #     super().clean()


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'avatar']


class SearchForm(forms.Form):
    search = forms.CharField()


class AdminImageWidget(forms.ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            t = get_thumbnail(value, '120x120')
            output.append('<img src="{}"/><br/>'.format(t.url))
        output.append(super().render(name, value, attrs, renderer))
        return mark_safe(u''.join(output))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'avatar']
        widgets = {'username': forms.TextInput(attrs={'readonly': 'readonly'}), 'avatar': AdminImageWidget}
