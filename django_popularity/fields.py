from django import forms
from django.db import models


class MIDWidget(forms.TextInput):
    template_name = 'django_popularity/mid.html'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {
            'readonly': 'readonly'
        })
        super().__init__(*args, **kwargs)


class MIDFormField(forms.CharField):
    widget = MIDWidget

    def __init__(self, **kwargs):
        kwargs['widget'] = self.widget()
        super().__init__(**kwargs)


class MIDField(models.CharField):

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', MIDFormField)
        return super().formfield(**kwargs)
