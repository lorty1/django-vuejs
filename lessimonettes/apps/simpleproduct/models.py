#!/usr/local/bin/python
# coding: utf-8
from django.db import models
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import datetime
from django.template.defaultfilters import slugify
from itertools import chain
#from customer.models import Customer
# Create your models here.

class Category(models.Model):
    '''
    Product category
    '''
    title = models.CharField(_(u'Titre'), max_length=250)
    slug = models.SlugField(
        _('slug'),
        max_length=256,
        help_text=_('Automatically built from the title. A slug is a short '
                    'label generally used in URLs.'),
    )
    date_added = models.DateTimeField(_(u'Ajouté'), auto_now_add=True)
    is_active = models.BooleanField(_(u'Actif'), default=False)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def save(self, *args, **kwargs):
        # Raise on circular reference
        if not self.slug:
            self.slug = slugify(str(self.title))
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class ProductType(models.Model):
    '''
    Product category
    '''
    title = models.CharField(_(u'Titre'), max_length=250)
    slug = models.SlugField(
        _('slug'),
        max_length=256,
        help_text=_('Automatically built from the title. A slug is a short '
                    'label generally used in URLs.'),
    )
    date_added = models.DateTimeField(_(u'Ajouté'), auto_now_add=True)
    is_active = models.BooleanField(_(u'Actif'), default=False)

    class Meta:
        verbose_name = _('Type de produit')
        verbose_name_plural = _('Types de produits')

    def save(self, *args, **kwargs):
        # Raise on circular reference
        if not self.slug:
            self.slug = slugify(str(self.title))
        super(ProductType, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class Product(models.Model):
    '''
    Product

    Base class to create a product
    '''
    category = models.ForeignKey(Category, help_text=_(u'Rangez ce produit dans une catégorie.'), blank=True, null=True, on_delete=models.CASCADE)
    product_type = models.ForeignKey(ProductType, help_text=_(u'Définissez le type du produit.'), blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(_(u'Titre'), max_length=250)
    product_title = models.CharField(_(u'Type de produit'), max_length=250)
    product_code = models.CharField(_(u'Code produit sur Odoo'), max_length=250, blank=True)
    slug = models.SlugField(
        _('slug'),
        max_length=256,
        help_text=_('Automatically built from the title. A slug is a short '
                    'label generally used in URLs.'),
    )
    description = models.TextField(_(u'Description'), max_length=2500, blank=True)
    max_number = models.IntegerField(_(u'Nombre de pièces maximum'), max_length=5, blank=True, null=True)
    number = models.IntegerField(_(u'Nombre de pièces'), max_length=5, blank=True, null=True)
    temp_number = models.IntegerField(_(u'Nombre de pièces temporaire'), max_length=5, blank=True, null=True)
    date_availability = models.DateField(_(u'Disponible en livraison à partir de'), null=True, blank=True)
    weight = models.PositiveIntegerField(_(u'Poids de la pièce en grammes'), max_length=5, blank=True, null=True)
    #customer = models.ManyToManyField(Customer, verbose_name='Marque', null=True, blank=True, related_name="product_customers")
    price = models.DecimalField(_(u'Tarif TTC'), max_digits=7, decimal_places=4, max_length=7, blank=True, null=True)
    is_active = models.BooleanField(_(u'Actif'), default=True)
    is_selected = models.BooleanField(_(u'Selectionné'),default=True,)
    date_added = models.DateTimeField(_(u'Ajouté'), auto_now_add=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def get_last_image(self):
        image = ProductImage.objects.filter(product=self).last()
        if image:
            response = str(image.image_thumbnail)
        else:
            response = ''
        return response

    def save(self, *args, **kwargs):
        # Raise on circular reference
        if not self.slug:
            self.slug = slugify(str(self.title)+'-'+str(self.pk))
        super(Product, self).save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey('Product', null=True, blank=True, on_delete=models.CASCADE)
    image_thumbnail = models.ImageField(_(u'Image miniature'), upload_to='static/images/simpleproduct/thumbnail/', blank=True, null=True)
    image_full = models.ImageField(_(u'Image complète'), upload_to='static/images/simpleproduct/full/', blank=True, null=True)
    caption = models.CharField(max_length=100, blank=True, verbose_name=_('caption')) 
    created_on = models.DateTimeField(_('date added'), auto_now_add=True)
    order = models.IntegerField(_(u'Ordre'), default=0)
     
    def save(self):
        if not self.created_on:
            self.created_on = datetime.now()
        super(ProductImage, self).save()
        
    def __unicode__(self):
        return str(self.image_full) + ' ' + self.created_on.strftime('%d/%m/%Y')

    def __str__(self):
        return str(self.image_full) + ' ' + self.created_on.strftime('%d/%m/%Y')

    def show_url(self):
        if self.image_full:
            return '<a href="/static/%s" target="_blank">Voir l\'image</a>' % (self.image_full)
        else:
            return u'Pas d\image'
    show_url.allow_tags = True

    def show_image_full(self):
        if self.image_full:
            return '<img src="/static/'+str(self.image_full)+'" />'
        else:
            return '<img src="/static/" />'
    show_image_full.allow_tags = True

    def show_image_thumbnail(self):
        if self.image_thumbnail:
            return '<img src="/static/'+str(self.image_thumbnail)+'" />'
        else:
            return '<img src="/static/" />'
    show_image_thumbnail.allow_tags = True

    class Meta:
        ordering = ['-created_on']
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
