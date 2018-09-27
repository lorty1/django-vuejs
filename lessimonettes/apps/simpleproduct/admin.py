from django.contrib import admin
from .models import Product, ProductImage, Category, ProductType
from easycheckout.models import Item
from django.db import models
from django.utils.safestring import mark_safe

from django.utils.translation import ugettext as _

from django.contrib.admin.widgets import AdminFileWidget
from django.core.mail import send_mail


class InlineProductAdmin(admin.TabularInline):
    extra = 1
    model = Product

class CategoryAdmin(admin.ModelAdmin):
    pass

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name=str(value)
            output.append(u' <a href="%s" target="_blank"><img src="/%s" alt="%s" width="150" height="150"  style="object-fit: cover;"/></a> %s ' % (image_url, image_url, file_name, _('')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class InlineProductImageAdmin(admin.TabularInline):
    extra = 1
    model = ProductImage
    formfield_overrides = {models.ImageField: {'widget': AdminImageWidget}}
    ordering = ('-created_on',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'product_code', 'slug', 'category', 'is_active')
    list_editable = ('category', 'product_code', 'slug', 'is_active')
    list_filter = ('category',)
    inlines = [InlineProductImageAdmin]
    class Media:
        js = ['/static/tinymce/js/tinymce/tinymce.min.js', '/static/tinymce/js/tinymce/jquery.tinymce.init.js']

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_thumbnail')
    #list_editable = ('image_square', 'image_full", "image_long', 'image_midlong')
    list_filter = ('product', 'product__category')

admin.site.register(ProductType)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
