#!/usr/local/bin/python
# coding: utf-8

from django import template

register = template.Library()

@register.filter
def divide(value):
    return float(value) / float(100)

@register.filter
def point(value):
    return str(value).replace(',', '.')
