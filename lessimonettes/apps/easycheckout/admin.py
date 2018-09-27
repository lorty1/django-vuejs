# Register your models here.
from django.contrib import admin
from daterange_filter.filter import DateRangeFilter
from .models import Order, Item, OrderCart, ItemCart, ShippingAddress, BillingAddress, Credit
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from datetime import datetime

#Sending html emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from import_export import resources
from import_export.admin import ImportExportModelAdmin

#from chronopost_ws.views import send_shipping
from import_export.fields import Field


def send_customers(modeladmin, request, queryset):
    users = []
    for q in queryset:
        users.append(q.user.email)
    users = sorted(set(users))
    users_list = ""
    for u in users:
        users_list += str(u)+"\r\n"
    send_mail(
       u'Liste des clients',
       u''+users_list,
       u'bonjour@envoiedusteak.fr',
       ['jeremie@envoiedusteak.fr',],
       fail_silently=False,
    ) 
send_customers.short_description = u"Envoyer les mails des clients"

def send_confirmed_order(modeladmin, request, queryset):
    for q in queryset:
        subject = u'Votre commande est validée'
        from_email = u'bonjour@envoiedusteak.fr'
        email_recipients = [q.user.email, 'jeremie@envoiedusteak.fr',]
        template_name = 'easycheckout/email/email_order_body.txt'
        html_template_name = 'easycheckout/email/email_order_body.html'

        html_content = render_to_string(html_template_name, {'order':str(q.pk), 'user':q.shipping_address.name}) # render with dynamic value
        text_content = strip_tags(html_template_name) # Strip the html tag. So people can see the pure text at least.

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to=email_recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
send_confirmed_order.short_description = u"Envoyer un mail de confirmation de la commande"



def send_heureux(modeladmin, request, queryset):
    for q in queryset:
        subject = u'Test mail confirmation commande'
        from_email = u'bonjour@envoiedusteak.fr'
        email_recipients = ['jeremie@envoiedusteak.fr',]
        template_name = 'easycheckout/email/email_order_body.txt'
        html_template_name = 'easycheckout/email/email_order_body.html'

        html_content = render_to_string(html_template_name, {'order':str(q.pk),}) # render with dynamic value
        text_content = strip_tags(html_template_name) # Strip the html tag. So people can see the pure text at least.

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to=email_recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
send_heureux.short_description = u"Test email order html"

def send_satisfaction(modeladmin, request, queryset):
    for q in queryset:
        subject = u'Alors heureuse/heureux ?'
        from_email = u'bonjour@envoiedusteak.fr'
        email_recipients = [q.user.email,]
        template_name = 'easyadvise/email/email_satisfaction_body.txt'
        html_template_name = 'easyadvise/email/email_satisfaction_body.html'

        html_content = render_to_string(html_template_name, {'order':str(q.pk), 'user':q.shipping_address.name}) # render with dynamic value
        text_content = strip_tags(html_template_name) # Strip the html tag. So people can see the pure text at least.

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to=email_recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
send_satisfaction.short_description = u"Envoyer le questionnaire"


def send_orders(modeladmin, request, queryset):
    for q in queryset:
        send_mail(
           u'Commande n°'+str(q.pk),
           u'Date de livraison prévue :'+str(q.delivery_date)+'\r\n'
           u'\r\n'
           u'Adresse de livraison :\r\n'
           u''+q.shipping_address.get_as_text()+'\r\n'
           u'\r\n'
           u'Email :\r\n'
           u''+q.user.email+'\r\n'
           u'\r\n'
           u'Résumé de la commande :\r\n'
           u''+q.get_items_as_text()+'\r\n'
           u'\r\n',
           u'bonjour@envoiedusteak.fr',
           ['jeremie@envoiedusteak.fr',],
           fail_silently=False,
        ) 
send_orders.short_description = u"Envoyer les commandes"


def recalculate_bill(modeladmin, request, queryset):
    for q in queryset:
        q.recalculate()
recalculate_bill.short_description = u"Recalculer la facture"

def make_bill(modeladmin, request, queryset):
    for q in queryset:
        q.create_odoo_invoice()
make_bill.short_description = u"Créer la facture"

class ItemResource(resources.ModelResource):
    order_number = Field()
    item_user = Field()
    item_category = Field()
    product = Field()
    product_title = Field()
    quantity = Field()
    basis_weight = Field()

    class Meta:
        model = Item
        fields = ('order_number', 'item_user', 'product', 'product_title', 'item_category', 'quantity', 'basis_weight')

    def dehydrate_order_number(self, item):
        return item.order.pk

    def dehydrate_item_user(self, item):
        return item.order.user

    def dehydrate_product(self, item):
        return item.product
    
    def dehydrate_quantity(self, item):
        return item.quantity

    def dehydrate_basis_weight(self, item):
        return item.basis_weight

    def dehydrate_product_title(self, item):
        return item.product.product_title

    def dehydrate_item_category(self, item):
        return item.product.category

class InlineItemAdmin(admin.TabularInline):
    extra = 1
    model = Item

class InlineItemCartAdmin(admin.TabularInline):
    extra = 1
    model = ItemCart

class CreditAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'total')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'date', 'is_paid', 'payment_status', 'delivery_date', 'shipping_address')
    inlines = [InlineItemAdmin]
    list_editable = ('delivery_date', 'shipping_address')
    list_filter = ['is_paid', 'payment_status', ('date', DateRangeFilter),]
    actions = [send_customers, send_orders, make_bill, send_satisfaction, send_heureux, send_confirmed_order]

class BillAdmin(admin.ModelAdmin):
    list_display = ('reference', 'order',)
    actions = [recalculate_bill]

class ItemAdmin(ImportExportModelAdmin):
    

    list_display = ('pk', 'show_order_number', 'show_item_user', 'product', 'show_product_title', 'show_item_category', 'quantity', 'basis_weight',)
    list_filter = ['order__payment_status',]
    resource_class = ItemResource


class OrderCartAdmin(admin.ModelAdmin):
    inlines = [InlineItemCartAdmin]


class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone_number', 'address1', 'address2', 'zip_code', 'city')

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone_number', 'address1', 'address2', 'zip_code', 'city')

admin.site.register(ItemCart)
admin.site.register(OrderCart, OrderCartAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(BillingAddress, BillingAddressAdmin)
