# -*- coding: utf-8 -*-

from django import forms


class AddFrom(forms.Form):
    date_text = forms.CharField()
    content_text = forms.CharField(max_length=200)
