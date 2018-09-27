# -*- coding: utf-8 -*-

from django.forms import ModelForm
from models import Block

class AddBlock(ModelForm):
    class Meta:
        model = Block
        exclude = ['created_on', 'moderated']

