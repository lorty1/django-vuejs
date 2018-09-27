# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.db import models
from mptt.admin import MPTTModelAdmin
try:
    from klingon.admin import TranslationInline, create_translations
except:
    pass
from .models import *

from django.utils.safestring import mark_safe

from django.utils.translation import ugettext as _

from django.contrib.admin.widgets import AdminFileWidget

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name=str(value)
            output.append(u' <a href="%s" target="_blank"><img src="/static/%s" alt="%s" width="150" height="150"  style="object-fit: cover;"/></a> %s ' % (image_url, image_url, file_name, _('')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class BlockMediaAdmin(admin.ModelAdmin):
    list_display = ('show_attachment', 'show_url')

class InlineBlockMediaAdmin(admin.TabularInline):
    extra = 1
    model = BlockMedia
    formfield_overrides = {models.FileField: {'widget': AdminImageWidget}}
    ordering = ('-created_on',)

class BlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'page', 'name', 'slug', 'moderated', 'published_on')
    list_editable = ('page', 'moderated', 'published_on')
    list_filter = ['page']
    inlines = [InlineBlockMediaAdmin]
    #inlines = [InlineBlockMediaAdmin, TranslationInline]
    #actions = [create_translations]
    class Media:
        js = ['/static/tinymce/js/tinymce/tinymce.min.js', '/static/tinymce/js/tinymce/jquery.tinymce.init.js']

class InlineBlockAdmin(admin.TabularInline):
    extra = 1
    model = Block
    ordering = ('-created_on',)
    prepopulated_fields = {'slug': ('name',)}
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows':3,'cols':30})}
    }

class PageAdmin(MPTTModelAdmin):
    change_list_template = 'pager/admin/change_list.html'
    inlines = [InlineBlockAdmin]
    ordering = ('title',)
    list_display = ('id', 'title', 'parent', 'url')
    list_editable = ('title', 'parent', 'url')
    list_filter = ['is_public']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'slug', 'description')

admin.site.register(Block, BlockAdmin)
admin.site.register(BlockMedia, BlockMediaAdmin)
admin.site.register(Page, PageAdmin)
#admin.site.register(BlockI18N)
