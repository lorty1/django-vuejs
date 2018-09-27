#!/usr/local/bin/python
# coding: utf-8

from django.db import models
from django.template.defaultfilters import slugify

from django.utils.translation import ugettext as _
from simpleproduct.models import *
from django.core.mail import send_mail


#Sending html emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

#try:
#    from django.contrib.auth import get_user_model
#except ImportError:
#    from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.utils.text import slugify

#import odoorpc
import datetime
from django.conf import settings
#from .odoo import *

STATUS = [
    (u'Validée', u'Validée'),
    (u'Annulée', u'Annulée'),
    (u'En cours', u'En cours'),
]
class BaseAddress(models.Model):
    """
    Base address

    BaseAddress class to create un new address
    """   

    user = models.ForeignKey(User, verbose_name="Utilisateur", on_delete=models.CASCADE)
    name = models.CharField(_(u"Nom et prénom*"), max_length=1024)
    phone_number = models.CharField(_(u'Numéro de téléphone*'), max_length=250)
    address1 = models.CharField(_("Adresse 1*"), max_length=1024)
    address2 = models.CharField(_("Adresse 2"), max_length=1024, blank=True, null=True)
    zip_code = models.CharField(_("Code postal*"), max_length=12)
    city = models.CharField(_("Ville*"), max_length=1024)
    country = models.CharField(_("Pays"), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('Addresse de livraison')
        verbose_name_plural = _('Adresses de livraison')

    def save(self, *args, **kwargs):
        super(BaseAddress, self).save()

    def __str__(self):
        return self.address1

    def get_as_html(self):
        """
        Return this comment as plain text. Useful for emails.
        """
        d = {
            'name': self.name,
            'address1': self.address1,
            'address2': self.address2,
            'zip_code': self.zip_code,
            'city': self.city,
            'phone': self.phone_number,
        }
        return ('<p>%(name)s<br/>'
                  '%(address1)s<br />'
                  '%(address2)s<br />'
                  '%(zip_code)s<br />'
                  '%(city)s<br/>'
                  '%(phone)s</p>') % d


    def get_as_text(self):
        """
        Return this comment as plain text. Useful for emails.
        """
        d = {
            'name': self.name,
            'address1': self.address1,
            'address2': self.address2,
            'zip_code': self.zip_code,
            'city': self.city,
            'phone': self.phone_number,
        }
        return ('%(name)s\r\n'
                  '%(phone)s\r\n'
                  '%(address1)s\r\n'
                  '%(address2)s\r\n'
                  '%(zip_code)s\r\n'
                  '%(city)s') % d

class ShippingAddress(BaseAddress):
    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")

class BillingAddress(BaseAddress):
    class Meta:
        verbose_name = _("Billing Address")
        verbose_name_plural = _("Billing Addresses")


class OrderManager(models.Manager):
    def create_order(self, user_pk, status):
        order = self.create(user=user_pk, status=status)
        return order

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="Utilisateur", on_delete=models.CASCADE)
    date = models.DateField(_(u'date'), auto_now=True, blank=True)
    status = models.CharField(_(u'Etat'), choices=STATUS, max_length=150, blank=True)
    total = models.IntegerField(_(u'Total'), blank=True, null=True, default=0)
    delivery_date = models.DateField(_(u'Date de livraison prévue'), blank=True, null=True)
    shipping_address = models.ForeignKey(ShippingAddress, verbose_name="Adresse de livraison*", null=True, blank=True, on_delete=models.CASCADE)
    billing_as_shipping = models.BooleanField(_(u'Utiliser l\'adresse de livraison comme adresse de facturation'), default=True)
    billing_address = models.ForeignKey(BillingAddress, verbose_name="Adresse de facturation", null=True, blank=True, on_delete=models.CASCADE)
    cgv = models.BooleanField(_(u'Valider les conditions générales de vente'), default=False)
    #use_credit = models.BooleanField(_(u'Je souhaite utiliser mon avoir'), default=False)
    is_paid = models.BooleanField(_(u'A été payée'), default=False)
    payment_status = models.CharField(_(u'Status du paiement'), max_length=250, blank=True)
    payment_auth_code = models.CharField(_(u'Code \'authorisation'), max_length=250, blank=True)

    objects = OrderManager()

    class Meta:
        verbose_name = _('Commande')
        verbose_name_plural = _('Commandes')

    def save(self, *args, **kwargs):
        self.total = self.total_amount()
        super(Order, self).save()
        remained = False
        if self.status == 'En cours':
            remained = False
        elif self.status == 'Annulée':
            remained = False
        else:
            remained = True
        super(Order, self).save()

    def __str__(self):
        return u'Commande {0}'.format(self.pk)


#    def get_advise(self):
#        from easyadvise.models import Advise
#        advise = Advise.objects.filter(order=self).first()
#        score = ''
#        if advise:
#            score = advise.score
#        return str(score)

    def get_bill(self):
        try:
            bill = Bill.objects.filter(order=self).first()
            return str(bill.id)
        except:
            pass

    def get_items(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """   
        items = Item.objects.filter(order=self)
        return items

    def get_items_as_text(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """  
        items = Item.objects.filter(order=self)
        items_text = ""
        for i in items:
            items_text += str(i.product.title)+' - Poids de la pièce : '+str(i.basis_weight)+'g - Quantité : x'+str(i.quantity)+'\r\n'
            #if i.orientation == 1 or i.orientation == 2:
            #    "Cowfunding"
        return items_text


    def get_total_weight(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """   
        items = Item.objects.filter(order=self)
        weight = 0
        for i in items:
            weight += i.quantity * i.basis_weight
        return weight

    def empty_order(self):
        """
        Function to empty the order
        Delete all items in relation with the order
            :param self: 

            Return:
                string: 
        """   
        items = Item.objects.filter(order=self)
        for i in items:
            i.delete()

    def total_product(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        return int(total*100)


class ItemManager(models.Manager):
    def create_item(self, order_pk, product_pk, quantity, basis_weight, orientation):
        item = self.create(order=order_pk, product=product_pk, quantity=quantity, basis_weight=basis_weight, orientation=orientation)
        return item

class Item(models.Model):
    order = models.ForeignKey(Order, verbose_name="Commande", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Produit", on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Quantité", default=1)
    basis_weight = models.PositiveIntegerField(verbose_name="Poids de la pièce", null=True, blank=True)

    objects = ItemManager()
    
    def save(self, *args, **kwargs):
        super(Item, self).save()

    def __str__(self):
        return self.product.title

    def get_price(self):
        return (self.quantity * self.product.price * self.basis_weight) / 1000

    def show_item_user(self):
        return self.order.user
    show_item_user.allow_tags = True

    def show_item_category(self):
        return self.product.category
    show_item_category.allow_tags = True
    
    def show_product_title(self):
        return self.product.product_title
    show_product_title.allow_tags = True

    def show_order_number(self):
        return self.order.pk
    show_order_number.allow_tags = True


class OrderCartManager(models.Manager):
    def create_order_cart(self, status):
        order = self.create(status=status)
        return order

class OrderCart(models.Model):
    date = models.DateField(_(u'date'), auto_now=True, blank=True)
    status = models.CharField(_(u'panier'), max_length=500, blank=True)
    total = models.IntegerField(_(u'Total'), blank=True, null=True, default=0)

    objects = OrderCartManager()

    class Meta:
        verbose_name = _('Panier')
        verbose_name_plural = _('Paniers')

    def save(self, *args, **kwargs):
        super(OrderCart, self).save()

    def __str__(self):
        return u'Panier {0}'.format(self.pk)

    def get_items(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """   
        items = ItemCart.objects.filter(order_cart=self)
        return items

    def get_total_weight(self):
        """
        Function to get all items from an order
            :param self: 

            Return:
                object: 
        """   
        items = ItemCart.objects.filter(order_cart=self)
        weight = 0
        for i in items:
            weight += i.quantity * i.basis_weight
        return weight

    def subtract_items(self):
        """
        Function to subtract weight to a muscle from each item
            :param self: 

            Return:
                string: 
        """   
        items = ItemCart.objects.filter(order_cart=self)
        for i in items:
            i.product.subtract_weight_to_product(int(i.product.weight))
            i.product.save()

    def empty_order(self):
        """
        Function to empty the order
        Delete all items in relation with the order
            :param self: 

            Return:
                string: 
        """   
        items = ItemCart.objects.filter(order_cart=self)
        for i in items:
            i.delete()

    def get_delivery(self):
        total = 0
        delivery = total
        return delivery

    def total_product(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        total += panier
        return int(total*100)

    def total_amount(self):
        """
        Function to calculate the total amount of an order
            :param self: 

            Return:
                int: 
        """   
        total = 0
        panier = 0
        return total

class ItemCartManager(models.Manager):
    def create_item_cart(self, order_cart_pk, product_pk, quantity, basis_weight, orientation):
        item = self.create(order_cart=order_cart_pk, product=product_pk, quantity=quantity, basis_weight=basis_weight, orientation=orientation)
        return item

class ItemCart(models.Model):
    order_cart = models.ForeignKey(OrderCart, verbose_name="Commande", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Produit", on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Quantité", default=1)
    basis_weight = models.PositiveIntegerField(verbose_name="Poids de la pièce", null=True, blank=True)

    objects = ItemCartManager()
    
    def save(self, *args, **kwargs):
        super(ItemCart, self).save()

    def __str__(self):
        return self.product.slug.replace('-none', '')

    def get_price(self):
        return (self.quantity * self.product.price * self.basis_weight) / 1000

class Credit(models.Model):
    reference = models.CharField(_(u'Référence'), max_length=20, blank=True)
    user = models.ForeignKey(User, verbose_name="Utilisateur", on_delete=models.CASCADE)
    date = models.DateField(_(u'date'), auto_now=True, blank=True)
    total = models.IntegerField(_(u'Total'), blank=True, null=True, default=0)

    def save(self, *args, **kwargs):
        super(Credit, self).save()

    def __str__(self):
        return self.reference
