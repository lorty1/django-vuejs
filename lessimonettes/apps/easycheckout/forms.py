from django.forms import ModelForm
from .models import Order, ShippingAddress, BillingAddress
from simpleproduct.models import Cow
from django import forms 
from django.contrib.auth.models import User
import datetime
import locale

HOURS_CHOICE = []
for i in range(8000):
    HOURS_CHOICE.append((i, str(i)))

def set_locale(locale_):
    locale.setlocale(category=locale.LC_ALL, locale=locale_)

class OrderForm(ModelForm):
    cgv = forms.BooleanField(label=u"Valider les conditions générales de vente", required=True)

    def __init__(self, user, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        # access object through self.instance...
        set_locale('fr_FR.utf8')

        self.fields['shipping_address'].queryset = ShippingAddress.objects.filter(user=user).order_by('id').reverse()
        self.fields['shipping_address'].empty_label = None
        self.fields['shipping_address'].required = True
        self.fields['billing_address'].queryset = BillingAddress.objects.filter(user=user).order_by('id').reverse()
        self.fields['billing_address'].empty_label = None

        self.fields['user'].queryset = User.objects.filter(pk=user.pk)
        self.initial['user'] = user

        
        user_order = Order.objects.filter(user=user).last()
        stock_date = datetime.datetime.today()
        for i in user_order.get_items():
            if i.orientation.pk == 3:
                date_availability = i.product.date_availability
                if date_availability:
                    date_availability = datetime.datetime.combine(i.product.date_availability, datetime.datetime.min.time())
                    date_availability = date_availability - datetime.timedelta(days=2)
                    if date_availability > stock_date:
                        stock_date = date_availability
                  

        #Si commande du lundi au jeudi ou dimanche (si precise), livraison à j+3 après 12h
        if stock_date.isoweekday() == 1 or stock_date.isoweekday() == 2 or stock_date.isoweekday() == 3 or stock_date.isoweekday() == 4 or stock_date.isoweekday() == 7:   
            if stock_date.hour > 10:
                stock_date = stock_date + datetime.timedelta(days=1)
        elif stock_date.isoweekday() == 5:
            stock_date = stock_date + datetime.timedelta(days=3)
        elif stock_date.isoweekday() == 6:
            stock_date = stock_date + datetime.timedelta(days=2)
             
        stock_date_list = []

        #hour_list = [(i, datetime.time(i).strftime('%H:%M')) for i in range(24)]
        hour_list = ''

        weekend = set([6])
        for i in range(7):
            is_new_date = True
            if i > 1:
                new_datetime = stock_date + datetime.timedelta(days=i)
                #new_date = datetime.datetime.strftime(new_datetime, '%A %d %B %Y')
                new_date = datetime.datetime.strftime(new_datetime, '%d-%m-%Y')
                if new_datetime.weekday() not in weekend:
                    new_date_consumption = new_datetime + datetime.timedelta(days=2)
                    for i in user_order.get_items():
                        if i.orientation.pk == 3:
                            product_date_consumption = datetime.datetime.combine(i.product.date_consumption, datetime.datetime.min.time())
                            product_date_consumption = product_date_consumption + datetime.timedelta(days=2)
                            if product_date_consumption <= new_date_consumption:
                                is_new_date = False
                                #print('False')
                                #print(i.product.date_consumption)
                                #print(product_date_consumption)
                                #print(new_date_consumption)
                    if is_new_date:
                        stock_date_list.append((new_datetime.strftime('%Y-%m-%d'), new_date))
        self.fields['wished_stock_delivery_date'] = forms.ChoiceField(choices = stock_date_list, label=u"Date de livraison souhaitée pour nos produits au détail", initial='', widget=forms.Select(), required=True)
        self.fields['wished_stock_delivery_hour'] = forms.ChoiceField(choices =HOURS_CHOICE, label=u"Heure de livraison souhaitée pour nos produits au détail", initial='', widget=forms.Select(), required=False)
        self.fields['wished_dry_delivery_date'] = forms.ChoiceField(choices = stock_date_list, label=u"Date de livraison souhaitée pour nos produits secs", initial='', widget=forms.Select(), required=True)
        self.fields['wished_dry_delivery_hour'] = forms.ChoiceField(choices = hour_list, label=u"Heure de livraison souhaitée pour nos produits secs", initial='', widget=forms.Select(), required=False)
 
        cowfunding = user_order.get_cowfunding_pk()
        cow = Cow.objects.get(pk=cowfunding)
        cowfunding_date = cow.date_shipping
        #try:
        #    cowfunding = user_order.get_cowfunding_pk()
        #    cow = Cow.objects.get(pk=cowfunding)
        #    cowfunding_date = cow.date_shipping
        #except:
        #    cowfunding_date = datetime.datetime.today()
        print(cowfunding_date)
        cowfunding_date_list = []
        weekend = set([6])
        for i in range(5):
            new_datetime = cowfunding_date + datetime.timedelta(days=i)
            new_date = datetime.datetime.strftime(new_datetime, '%A %d %B %Y')
            if new_datetime.weekday() not in weekend:
                cowfunding_date_list.append((new_datetime, new_date))
 
        self.fields['wished_cf_delivery_date'] = forms.ChoiceField(choices = cowfunding_date_list, label=u"Date de livraison souhaitée pour nos produits Cowfunding", initial='', widget=forms.Select(), required=True)
        self.fields['wished_cf_delivery_hour'] = forms.ChoiceField(label=u"Heure de livraison souhaitée pour nos produits Cowfunding", initial='', widget=forms.Select(), required=False)
        self.fields['wished_cf_delivery_hour'] = forms.ChoiceField(choices=HOURS_CHOICE, label=u"Heure de livraison souhaitée pour nos produits Cowfunding", initial='', widget=forms.Select(), required=False)

    class Meta:
        model = Order
        fields = ['user', 'shipping_address', 'billing_as_shipping', 'billing_address', 'wished_cf_delivery_date', 'use_precise_for_cf', 'wished_cf_delivery_hour', 'wished_stock_delivery_date', 'use_precise_for_stock', 'wished_stock_delivery_hour', 'wished_dry_delivery_date', 'cgv', 'use_credit']

class ShippingAddressForm(ModelForm):
    name = forms.CharField(label=u'Nom et prénom', widget=forms.TextInput(attrs={'placeholder': 'Nom et prénom'}))
    phone_number = forms.CharField(label=u'Numéro de téléphone*', widget=forms.TextInput(attrs={'placeholder': u'Numéro de téléphone'}))
    address1 = forms.CharField(label='Adresse 1', widget=forms.TextInput(attrs={'placeholder': 'Addresse'}))
    address2 = forms.CharField(label='Adresse 2',widget=forms.TextInput(attrs={'placeholder': u'Complément d\'adresse'}) )
    zip_code = forms.CharField(label='Code postal', widget=forms.TextInput(attrs={'placeholder': 'Code postal'}))
    city = forms.CharField(label='Ville', widget=forms.TextInput(attrs={'placeholder': 'Ville'}))
    country = forms.CharField(label='Pays', widget=forms.TextInput(attrs={'placeholder': 'PaysSearch'}))

    def __init__(self, user, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        # access object through self.instance...
        #self.fields['user'].queryset = User.objects.filter(pk=user.pk)

    class Meta:
        model = ShippingAddress
        exclude = ['user',]
        fields = ['name', 'phone_number', 'address1', 'address2', 'zip_code', 'city', 'country']

class BillingAddressForm(ModelForm):
    name = forms.CharField(label=u'Nom et prénom', widget=forms.TextInput(attrs={'placeholder': 'Nom et prénom'}))
    phone_number = forms.CharField(label=u'Numéro de téléphone*', widget=forms.TextInput(attrs={'placeholder': u'Numéro de téléphone'}))
    address1 = forms.CharField(label='Adresse 1', widget=forms.TextInput(attrs={'placeholder': 'Addresse'}))
    address2 = forms.CharField(label='Adresse 2',widget=forms.TextInput(attrs={'placeholder': u'Complément d\'adresse'}) )
    zip_code = forms.CharField(label='Code postal', widget=forms.TextInput(attrs={'placeholder': 'Code postal'}))
    city = forms.CharField(label='Ville', widget=forms.TextInput(attrs={'placeholder': 'Ville'}))
    country = forms.CharField(label='Pays', widget=forms.TextInput(attrs={'placeholder': 'PaysSearch'}))

    def __init__(self, user, *args, **kwargs):
        super(BillingAddressForm, self).__init__(*args, **kwargs)
        # access object through self.instance...
        #self.fields['user'].queryset = User.objects.filter(pk=user.pk)
        
    class Meta:
        model = BillingAddress
        exclude = ['user',]
        fields = ['name', 'phone_number', 'address1', 'address2', 'zip_code', 'city', 'country']
