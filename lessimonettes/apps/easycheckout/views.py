# coding: utf-8

from datetime import datetime
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import CreateView, DeleteView
from django.contrib.auth import authenticate, login, logout
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from easydiscount.models import Discount
from chronopost_ws.views import send_shipping 
import zeep
from zeep import xsd
import json

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from ipware.ip import get_ip
from django.shortcuts import redirect

from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail


#Sending html emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Order, OrderCart, Item, ItemCart, Credit, ShippingAddress, BillingAddress, Bill
from .serializers import ShippingAddressSerializer, BillingAddressSerializer, OrderSerializer, OrderCartSerializer, ItemCartSerializer
from simpleproduct.models import Product
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import hashlib
import pytz
import base64
import binascii
from pythonPaybox.Paybox import Transaction
from simpleproduct.models import Orientation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import OrderForm, ShippingAddressForm, BillingAddressForm
from cart.views import Cart


class ShippingCreate(CreateView):
    model = ShippingAddress
    success_url = '/commande/resume/'
    fields = ['user', 'name', 'phone_number', 'address1', 'address2', 'zip_code', 'city', 'country']

class BillingCreate(CreateView):
    model = BillingAddress
    success_url = '/commande/resume/'
    fields = ['user', 'name', 'phone_number', 'address1', 'address2', 'zip_code', 'city', 'country']

class ShippingDelete(DeleteView):
    model = ShippingAddress
    success_url = '/commande/profile/'

class BillingDelete(DeleteView):
    model = BillingAddress
    success_url = '/commande/profile/'

class OrderListView(ListView):
    '''
    OrderList
    '''
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        #context['orders'] = Order.objects.filter(user=self.request.user).filter(status="Terminée")
        #print(self.request.user)
        if self.request.user.is_superuser:
            orders = Order.objects.all()
        else:
            if self.request.user.is_authenticated():
                orders = Order.objects.filter(user=self.request.user).filter(status=u"Validée")
            else:
                orders = ''

        paginator = Paginator(orders, 25) # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            orders = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            orders = paginator.page(paginator.num_pages)
        context['orders'] = orders
        return context

class OrderDetailView(DetailView):
    '''
    OrderDetailView
    '''

    model = Order
    template_name = 'easycheckout/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['object_list'] = Order.objects.all()
        return context

class OrderSuccess(TemplateView):
    template_name = 'easycheckout/accepted_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super(OrderSuccess, self).get_context_data(**kwargs)
        order = Order.objects.filter(user=self.request.user, payment_status="Success").first()
        context['order'] = order 
        return(context)


class CartResume(TemplateView):
    '''
    CartResume
    '''
    template_name = 'easycheckout/cart_resume.html'

    def get_context_data(self, **kwargs):
        context = super(CartResume, self).get_context_data(**kwargs)
        context['path'] = self.request.path
 
        cart = Cart(self.request)
        #Check if order exists
        ip = get_ip(self.request)
        order_cart = OrderCart.objects.filter(status=ip).first()
        if not order_cart:
            order_cart = OrderCart.objects.create_order_cart(status=ip)

        #Create items in order
        order_cart.empty_order()
        for i in cart.list_items():
            wei = 0
            if i.basis_weight=='':
                wei = 100
            else:
                wei = i.basis_weight
            ort = ''
            if i.orientation=='':
                ort = Orientation.objects.first()
            else:
                ort = Orientation.objects.get(pk=i.orientation)
            item_cart = ItemCart.objects.create_item_cart(order_cart, i.obj, i.quantity, wei, ort)
        order_cart.total_amount()
        context['order'] = order_cart
        return(context)


class PayResume(TemplateView):
    '''
    PayResume
    '''

    template_name = 'easycheckout/order_resume.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        user = self.request.user 
        form = OrderForm(user, request.POST)
        #if form.is_valid():
        if form:
            order_pk = request.POST['order']
            try:
                billing_address = BillingAddress.objects.filter(pk=int(request.POST['billing_address'])).first()
            except:
                billing_address = None
            shipping_address = ShippingAddress.objects.filter(pk=int(request.POST['shipping_address'])).first()
            try:
                billing_as_shipping = request.POST['billing_as_shipping']
                if str(billing_as_shipping) == "on":
                    billing_as_shipping = True
            except:
                billing_as_shipping = False
            cgv = request.POST['cgv']
            if str(cgv) == "on":
                cgv = True
            try: 
                credit = request.POST['use_credit']
                if credit == "on":
                    credit = True
            except:
                credit = False
            order = Order.objects.get(pk=order_pk)
            try:
                if request.POST['use_precise_for_cf'] == "true":
                    order.use_precise_for_cf = True
            except:
                order.use_precise_for_cf = False
            try:
                if request.POST['use_precise_for_stock'] == "true":
                    order.use_precise_for_stock = True
            except:
                order.use_precise_for_stock = False
            order.wished_cf_delivery_date = request.POST['wished_cf_delivery_date']
            try:
                order.wished_cf_delivery_hour = request.POST['wished_cf_delivery_hour']
            except:
                pass
            try:
                order.wished_stock_delivery_date = request.POST['wished_stock_delivery_date']
            except:
                pass
            try:
                order.wished_stock_delivery_hour = str(request.POST['wished_stock_delivery_hour'])
            except:
                pass
            try:
                order.wished_dry_delivery_date = request.POST['wished_dry_delivery_date']
            except:
                pass
            try:
                order.wished_dry_delivery_hour = str(request.POST['wished_dry_delivery_hour'])
            except:
                pass
            order.cgv = cgv
            order.use_credit = credit
            order.billing_address = billing_address
            order.shipping_address = shipping_address
            order.billing_as_shipping = billing_as_shipping
            order.save(commit=False)
            return redirect('/commande/payer/')
        else:
            context['form' ] = form
            return super(PayResume, self).render_to_response(context)

    #def get(self, request):
    #    if self.request.user.is_anonymous():
    #        return redirect('/session-expire/')
    #    else:
    #        return self.get_context_data()

    def get_context_data(self, **kwargs):
        context = super(PayResume, self).get_context_data(**kwargs)
       


        context['path'] = self.request.path
        #Check if order exists
        order = Order.objects.filter(user=self.request.user, status="En cours").first()
        if order:
            if not order.shipping_address:
                shipping_address = ShippingAddress.objects.filter(user=self.request.user).last()
                if shipping_address:
                    order.shipping_address = shipping_address
                    order.save()
        if not order:
            shipping_address = ShippingAddress.objects.filter(user=self.request.user).last()
            order = Order.objects.create_order(self.request.user, status="En cours")
            if shipping_address:
                order = Order.objects.get(user=self.request.user, status="En cours")
                order.shipping_address = shipping_address
                order.save()
                
        order.use_precise_for_cf = False
        order.use_precise_for_stock = False

        #Create items in order
        cart = Cart(self.request)
        order.empty_order()
        for i in cart.list_items():
            wei = 0
            if i.basis_weight=='':
                wei = 100
            else:
                wei = i.basis_weight
            ort = ''
            if i.orientation=='':
                ort = Orientation.objects.first()
            else:
                ort = Orientation.objects.get(pk=i.orientation)
            item = Item.objects.create_item(order, i.obj, i.quantity, wei, ort)

        #Create payment
        #print('Total ='+str(order.total_amount()))
        order_total = int(order.total_amount())
        #order_total = str(order_total/10).replace('.', '')
        #order_total = int(order_total)
       
        try:
            credit = Credit.objects.get(user=self.request.user)
        except:
            credit = ''

        context['credit'] = credit

        user = self.request.user 
        #print(self.request.user)
        context['billing_form'] = ShippingAddressForm(user)
        context['shipping_form'] = BillingAddressForm(user)
        context['form'] = OrderForm(user)
        context['order'] = order
        return(context)

class ProfileView(TemplateView):
    '''
    PayView
    '''

    template_name = 'easycheckout/order_profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        user = self.request.user 
        credit = Credit.objects.filter(user=user)
        avoirs = 0
        for c in credit:
            avoirs += c.total
        #print(self.request.user)
        context['shipping_addresses'] = ShippingAddress.objects.filter(user=user)
        context['billing_addresses'] = BillingAddress.objects.filter(user=user)
        context['billing_form'] = ShippingAddressForm(user)
        context['shipping_form'] = BillingAddressForm(user)
        context['avoirs'] = avoirs
        return context

class AccountView(TemplateView):
    '''
    PayView
    '''

    template_name = 'easycheckout/order_account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        return context

class BillDetailView(DetailView):
    '''
    PayView
    '''
    model = Bill
    template_name = 'easycheckout/bill_detail.html'

    def get_context_data(self, **kwargs):
        context = super(BillDetailView, self).get_context_data(**kwargs)
        return context

class PayView(TemplateView):
    '''
    PayView
    '''

    template_name = 'easycheckout/order_pay.html'

    def get_context_data(self, **kwargs):
        context = super(PayView, self).get_context_data(**kwargs)
        context['path'] = self.request.path

        order = Order.objects.filter(user=self.request.user, status="En cours").first()
        order_total = int(order.total_amount())
        #order_total = str(order_total/10).replace('.', '')
        #order_total = int(order_total)
        order_email = self.request.user.email
        order_date = datetime.now()
        order_reference = order.pk
        transaction = Transaction(
              production = True,
              PBX_TOTAL = order_total,    # total of the transaction, in cents (10€ == 1000) (int)
              PBX_PORTEUR = str(order_email),  # customer's email address
              PBX_TIME = order_date,      # datetime object
              PBX_CMD = str(order_reference),   # order_reference (str)
          )
        form_values = transaction.post_to_paybox()

        context['order'] = order

        context['paybox_form'] = transaction.construct_html_form()
        context['action'] = form_values['action']
        context['mandatory'] = form_values['mandatory']
        context['accessory'] = form_values['accessory']
 
        return context

class LoginView(TemplateView):
    '''
    LoginView
    '''

    template_name = 'easycheckout/order_login.html'

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        return context

    def post(self, request, episode_slug, day, month, year, hour):
        '''
        Post Login form
        '''
        #print("post test")
        #print(request)
        
        email = request.POST.get('email', False)
        password = request.POST.get('password', False)
        user = authenticate(email=email, password=password)
        #print(user)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        return render(request, self.template_name)

class LogoutView(TemplateView):
    '''
    LogoutView
    '''
    template_name = 'easycheckout/order_logout.html'

    def get(self, request, **kwargs):
        '''
        Paid def view
        '''
        logout(request)
        return render(request, self.template_name)


class PaidView(TemplateView):
    '''
    PaidView
    '''
    template_name = 'service_booking/booking_paid.html'

    def get_context_data(self, **kwargs):
        context = super(PaidView, self).get_context_data(**kwargs)
        return context

def ipn(request):
    # Your order object
    order = get_object_or_404(Order, pk=request.GET.get('RE'))
    
    transaction = Transaction()
    notification = transaction.verify_notification(response_url=request.get_full_path(), order_total=order.total)

    if notification['success'] and order.is_paid == False:
        order.subtract_items()

    if notification["success"]:
        order.status = u'Validée'              # Boolea
        try:
            categories = order.categories()
            if len(categories) > 1:
                for i in order.categories():
                    if order.whished_cf_delivery_date != order.whished_stock_delivery_date:
                        send_shipping(order.pk, i)
            else:
                send_shipping(order.pk, categories[0])
        except:
            pass
    else:
        order.status = u'Annulée'              # Boolean
    #order.is_paid = notification['success']              # Boolean
    order.payment_status = notification['status']        # Paybox Status Message
    order.payment_auth_code = notification['auth_code'] # Authorization Code returned by Payment Center
    order.save()
    
    if notification['success'] and order.is_paid == False:
        credit_to_bill = 0
        if order.use_credit:
            credit = Credit.objects.filter(user=order.user).first()
            if credit.total >= order.total_amount():

                cowfunding_delivery = order.calculate_cowfunding_delivery()
                stock_delivery = order.calculate_stock_delivery()
                dry_delivery = order.calculate_dry_delivery()

                delivery = cowfunding_delivery + stock_delivery + dry_delivery

                credit_to_bill = int(order.total_product() + (int(delivery)*100)) - 700
                new_credit = int(credit.total) - int(order.total_product() + (int(delivery)*100)) + 700
                credit.total = new_credit
            else:
                credit_to_bill = credit.total
                credit.total = 0
            credit.save()

        try:
            discounts = Discount.objects.filter(godfather=order.user).first()
            if not discounts:
                import uuid
                unique_code = int(str(uuid.uuid4().fields[-1])[:8])
                test_code = Discount.objects.filter(code=unique_code).first()
                if test_code:
                    unique_code = int(str(uuid.uuid4().fields[-1])[:8])
                discount = Discount.objects.create(code=unique_code, discount=0.0, godfather=order.user, godfather_discount=0.0, used_number=1, is_newuser=True)
                discount.save()
        except:
            pass

        try:
            subject = u'Votre commande '+str(order.pk)+u' sur Envoiedusteak.fr est validée',
            from_email = u'bonjour@envoiedusteak.fr'
            email_recipients = [order.user.email,'jeremie@envoiedusteak.fr']
            template_name = 'easycheckout/email/email_order_body.txt'
            html_template_name = 'easycheckout/email/email_order_body.html'

            html_content = render_to_string(html_template_name, {'order':str(order.pk), 'user':str(order.shipping_address.name)}) # render with dynamic value
            text_content = strip_tags(html_template_name) # Strip the html tag. So people can see the pure text at least.

        # create the email, and attach the HTML version as well.
            msg = EmailMultiAlternatives(subject, text_content, from_email, to=email_recipients)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except:
            send_mail(
                u'Votre commande '+str(order.pk)+' sur Envoiedusteak.fr est validée',
                u'BONJOUR '+str(order.shipping_address.name)+',\r\n\r\nMerci pour votre commande sur envoiedusteak.fr\r\nVous retrouverez les détails et le suivi de cette commande sur: https://www.envoiedusteak.fr/commande/liste/ \r\nLorsque votre commande sera prise en charge par notre partenaire Chronofresh, vous recevrez une confirmation par mail avec un numéro de suivi.\r\nVous n\'êtes pas là le jour de la livraison ? Pas de panique ! Vous pouvez reprogrammer une livraison avec Chronofresh.\r\nAllez, à nous d\'envoyer maintenant !',
                u'bonjour@envoiedusteak.fr',
                [order.user.email,],
                fail_silently=False,
            ) 



        #send_mail(
        #   u'Votre commande '+str(order.pk)+' sur Envoiedusteak.fr est validée',
        #   u'BONJOUR '+str(order.shipping_address.name)+',\r\n\r\nMerci pour votre commande sur envoiedusteak.fr\r\nVous retrouverez les détails et le suivi de cette commande sur: https://www.envoiedusteak.fr/commande/liste/ \r\nLorsque votre commande sera prise en charge par notre partenaire Chronofresh, vous recevrez une confirmation par mail avec un numéro de suivi.\r\nVous n\'êtes pas là le jour de la livraison ? Pas de panique ! Vous pouvez reprogrammer une livraison avec Chronofresh.\r\nAllez, à nous d\'envoyer maintenant !',
        #   u'bonjour@envoiedusteak.fr',
        #   [order.user.email,],
        #   fail_silently=False,
        #) 

        #date = datetime.today()
        #bills = Bill.objects.all()
        #bill_id = len(bills)
        #bill_id = "%02d" % (bill_id)
        #bill = Bill(reference="SAJ/"+str(date.year)+"/"+str(bill_id), order=order, credit=credit_to_bill)  
        #bill.save()
    
    # Paybox Requires a blank 200 response
    return HttpResponse('')



@api_view(['GET', 'POST'])
@csrf_exempt
@ensure_csrf_cookie
class UpdateOrder(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.shipping_address = self.request.data.get("shipping_address")
        instance.billing_address = self.request.data.get("billing_address")
        instance.save()

        serializer = self.get_serializer(instance)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


def get_cf_precise(self, pk):
    

    accountNumber = '19869502'
    password = '255562'
    callerTool='RDVWS'
    productType='FRESH'
    shipperZipCode=47000
    shipperCountry='FR'
    recipientZipCode=47000
    recipientCountry='FR'
    dateBegin=  datetime.strptime("2018-05-05T00:00:00.000z", "%Y-%m-%dT%H:%M:%S.%fZ")
    dateEnd=  datetime.strptime("2018-06-05T00:00:00.000z", "%Y-%m-%dT%H:%M:%S.%fZ")
    isDeliveryDate='true'
 
    instance = get_object_or_404(Order, pk=pk)
    shipperZipCode = instance.shipping_address.zip_code     
    recipientZipCode = instance.shipping_address.zip_code     
    try:
        cowfunding = instance.get_cowfunding_pk()
        cowfunding_date = cowfunding.date_shipping
        #TODO
        #Write correct date
        dateBegin=  datetime.strptime(cowfunding_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        dateEnd=  datetime.strptime("2018-06-05T00:00:00.000z", "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        dateBegin=  datetime.strptime("2018-05-05T00:00:00.000z", "%Y-%m-%dT%H:%M:%S.%fZ")
        dateEnd=  datetime.strptime("2018-06-05T00:00:00.000z", "%Y-%m-%dT%H:%M:%S.%fZ")

    wsdl = 'https://ws.chronopost.fr/rdv-cxf/services/CreneauServiceWS?wsdl'
    client = zeep.Client(wsdl=wsdl)
    header = xsd.Element(
        '{http://schemas.xmlsoap.org/soap/envelope/}Header',
        xsd.ComplexType([
        xsd.Element(
           '{http://cxf.soap.ws.creneau.chronopost.fr/}accountNumber',
           xsd.String()),
        xsd.Element(
           '{http://cxf.soap.ws.creneau.chronopost.fr/}password',
           xsd.String()),
        ])
    )
    header_value = header(accountNumber=accountNumber, password=password)

    data = client.service.searchDeliverySlot(callerTool='RDVWS',productType='FRESH',shipperZipCode='47000',shipperCountry="FR",recipientZipCode='33000',recipientCountry='FR',dateBegin=dateBegin,dateEnd=dateEnd,isDeliveryDate=True, _soapheaders=[header_value])
    input_dict = zeep.helpers.serialize_object(data)
    output_dict = json.loads(json.dumps(input_dict))
    return JsonResponse(output_dict)

def get_order_prices(self, pk):
    instance = get_object_or_404(Order, pk=pk)
    
    weight = instance.get_total_weight()     
    complements = instance.total_complements()     
    total_product = instance.total_product()     
    total_amount = instance.total_amount()     
    cowfunding_delivery = instance.calculate_cowfunding_delivery()     
    dry_delivery = instance.calculate_dry_delivery()     
    stock_delivery = instance.calculate_stock_delivery()     
    delivery = instance.get_delivery()     
 
    return JsonResponse({"weight":weight,
                         "total_complements":complements, \
                         "total_stocks":complements, \
                         "total_conserves":complements, \
                         "total_product":total_product, \
                         "total_amount":total_amount, \
                         "stocks_delivery":stock_delivery, \
                         "cowfunding_delivery":cowfunding_delivery, \
                         "delivery":delivery, \
                        })


def get_prices(self, pk):
    instance = get_object_or_404(OrderCart, pk=pk)
    
    weight = instance.get_total_weight()     
    complements = instance.total_complements()     
    total_product = instance.total_product()     
    total_amount = instance.total_amount()     
    cowfunding_delivery = instance.calculate_cowfunding_delivery()     
    dry_delivery = instance.calculate_dry_delivery()     
    stock_delivery = instance.calculate_stock_delivery()     
    delivery = instance.get_delivery()     
 
    return JsonResponse({"weight":weight,
                         "total_complements":complements, \
                         "total_stocks":complements, \
                         "total_conserves":complements, \
                         "total_product":total_product, \
                         "total_amount":total_amount, \
                         "stocks_delivery":stock_delivery, \
                         "cowfunding_delivery":cowfunding_delivery, \
                         "delivery":delivery, \
                        })

class GetOrderCartView(APIView):

    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(OrderCart, pk=kwargs['pk'])
        output_serializer = OrderCartSerializer(instance.get_items())
        
        return Response(output_serializer.data)


class GetShippingAddressView(APIView):

    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(ShippingAddress, pk=kwargs['pk'])
        output_serializer = ShippingAddressSerializer(instance)
        return Response(output_serializer.data)

class GetBillingAddressView(APIView):

    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(BillingAddress, pk=kwargs['pk'])
        output_serializer = BillingAddressSerializer(instance)
        return Response(output_serializer.data)



@api_view(['GET', 'POST'])
@csrf_exempt
@ensure_csrf_cookie
def update_order(request):
    #print("Update order")
    if request.method == 'POST':
        #print("Post datas")
        data_order = request.data.get('order')
        #print(data_order)
        data_shipping_address = request.data.get('shipping_address')
        shipping_address = ShippingAddress.objects.filter(pk=data_shipping_address).first()
        data_billing_address = request.data.get('billing_address')
        try:
            billing_address = BillingAddress.objects.filter(pk=data_billing_address).first()
        except:
            billing_address = None
        use_precise_for_cf = request.data.get('use_precise_for_cf')
        use_precise_for_stock = request.data.get('use_precise_for_stock')
        if use_precise_for_cf == None:
            use_precise_for_cf = False
        else:
            use_precise_for_cf = True
        if use_precise_for_stock == None:
            use_precise_for_stock = False
        else:
            use_precise_for_stock = True
        wished_cf_delivery_date = request.data.get('wished_cf_delivery_date')
        wished_stock_delivery_date = request.data.get('wished_stock_delivery_date')
        wished_dry_delivery_date = request.data.get('wished_dry_delivery_date')
        if wished_cf_delivery_date:
            try:
                wished_cf_delivery_date = datetime.strptime(wished_cf_delivery_date, '%Y-%m-%d')
            except:
                wished_cf_delivery_date = datetime.strptime(wished_cf_delivery_date, '%Y-%m-%d %H:%M:%S.%f')
        if wished_stock_delivery_date:
            wished_stock_delivery_date = datetime.strptime(wished_stock_delivery_date, '%Y-%m-%d')
        if wished_dry_delivery_date:
            wished_dry_delivery_date = datetime.strptime(wished_dry_delivery_date, '%Y-%m-%d')
        wished_cf_delivery_hour = request.data.get('wished_cf_delivery_hour')
        wished_stock_delivery_hour = request.data.get('wished_stock_delivery_hour')
        #wished_dry_delivery_hour = request.data.get('wished_dry_delivery_hour')
        if wished_cf_delivery_hour:
            wished_cf_delivery_hour = str(wished_cf_delivery_hour)
        if wished_stock_delivery_hour:
            wished_stock_delivery_hour = str(wished_stock_delivery_hour)
        #if wished_dry_delivery_hour:
        #    wished_dry_delivery_hour = str(wished_dry_delivery_hour)

        order = Order.objects.get(pk=data_order)
        order.shipping_address = shipping_address
        order.billing_address = billing_address
        order.use_precise_for_cf = use_precise_for_cf
        order.use_precise_for_stock = use_precise_for_stock
        #order.use_precise_for_dry = use_precise_for_dry
        order.wished_cf_delivery_date = wished_cf_delivery_date
        order.wished_cf_delivery_hour = wished_cf_delivery_hour
        order.wished_stock_delivery_date = wished_stock_delivery_date
        order.wished_stock_delivery_hour = wished_stock_delivery_hour
        order.wished_dry_delivery_date = wished_dry_delivery_date
        #Wait for stock and dry
        order.save()
        return HttpResponse("Address changed")

@api_view(['GET', 'POST'])
@csrf_exempt
@ensure_csrf_cookie
def create_shipping_address(request):
    if request.method == 'POST':
        data = {'user': request.data.get('user'),
                'name': request.data.get('name'),
                'phone_number': request.data.get('phone_number'),
                'address1': request.data.get('address1'),
                'address2': request.data.get('address2'),
                'zip_code': request.data.get('zip_code'),
                'city': request.data.get('city'),
                'country': request.data.get('country')}
        serializer = ShippingAddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        #print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@csrf_exempt
@ensure_csrf_cookie
def create_billing_address(request):
    if request.method == 'POST':
        #print("post address")
        data = {'user': request.data.get('user'),
                'name': request.data.get('name'),
                'phone_number': request.data.get('phone_number'),
                'address1': request.data.get('address1'),
                'address2': request.data.get('address2'),
                'zip_code': request.data.get('zip_code'),
                'city': request.data.get('city'),
                'country': request.data.get('country')}
        serializer = BillingAddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        #print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def update_cart(request):
    cart = Cart(request)
    #Check if order exists
    ip = get_ip(request)
    order_cart = OrderCart.objects.filter(status=ip).first()
    if not order_cart:
        order_cart = OrderCart.objects.create_order_cart(status=ip)

        #Create items in order
    order_cart.empty_order()
    for i in cart.list_items():
        wei = 0
        if i.basis_weight=='':
            wei = 100
        else:
            wei = i.basis_weight
        ort = ''
        if i.orientation=='':
            ort = Orientation.objects.first()
        else:
            ort = Orientation.objects.get(pk=i.orientation)
        item_cart = ItemCart.objects.create_item_cart(order_cart, i.obj, i.quantity, wei, ort)
    order_cart.total_amount()
    order_cart.save()
    #return HttpResponseRedirect('https://www.envoiedusteak.fr/commande/panier/')

@csrf_exempt
def remove_order_cart(request, pk):
    item = ItemCart.objects.get(pk=pk)
    item.delete() 

def update_order_cart(request):
        #Check if order exists
    order = Order.objects.filter(user=request.user, status="En cours").first()
    if not order:
        order = Order.objects.create_order(request.user, status="En cours")

    #Create items in order
    cart = Cart(request)
    order.empty_order()
    for i in cart.list_items():
        wei = 0
        if i.basis_weight=='':
            wei = 100
        else:
            wei = i.basis_weight
        ort = ''
        if i.orientation=='':
            ort = Orientation.objects.first()
        else:
            ort = Orientation.objects.get(pk=i.orientation)
        item = Item.objects.create_item(order, i.obj, i.quantity, wei, ort)

    #Create payment
    #print('Total ='+str(order.total_amount()))
    order_total = int(order.total_amount())
    order_total = str(order_total/10).replace('.', '')
    order_total = int(order_total)
    return HttpResponseRedirect('https://www.envoiedusteak.fr/commande/resume/')
