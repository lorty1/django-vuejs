from django.conf.urls import url
from django.views.generic import TemplateView
from rest_framework import routers
from django.contrib.auth.decorators import login_required
from .views import OrderDetailView, OrderListView, LoginView, LogoutView,\
                   PayResume, AccountView, CartResume, PayView, PaidView, update_order, UpdateOrder, update_cart, update_order_cart, ShippingCreate, BillingCreate,\
                   create_billing_address, create_shipping_address, ipn, ProfileView, BillDetailView, GetBillingAddressView, GetShippingAddressView, remove_order_cart, GetOrderCartView, get_prices, get_order_prices, get_cf_precise, OrderSuccess,\
                   ShippingDelete, BillingDelete


urlpatterns = [
    url(r'^$', OrderListView.as_view(), name='booking-room-list'),
    #url(r'^create/$', create_order),
    url(r'^login/$', LoginView.as_view()),
    url(r'^account/$', AccountView.as_view()),
    url(r'^profile/$', ProfileView.as_view()),
    url(r'^resume/$', PayResume.as_view()),
    url(r'^panier/$', CartResume.as_view()),
    url(r'^liste/$', OrderListView.as_view()),
    url(r'^address/create_shipping/$', ShippingCreate.as_view()),
    url(r'^address/create_billing/$', BillingCreate.as_view()),
    url(r'^address/shipping/delete/(?P<pk>[-\w]+)/$', ShippingDelete.as_view()),
    url(r'^address/billing/delete/(?P<pk>[-\w]+)/$', BillingDelete.as_view()),
    url(r'^api/shipping_address/(?P<pk>[-\w]+)/$', GetShippingAddressView.as_view()),
    url(r'^api/billing_address/(?P<pk>[-\w]+)/$', GetBillingAddressView.as_view()),
    url(r'^api/get_order_cart/(?P<pk>[-\w]+)/$', GetOrderCartView.as_view()),
    url(r'^api/get_prices/(?P<pk>[-\w]+)/$', get_prices),
    url(r'^api/get_order_prices/(?P<pk>[-\w]+)/$', get_order_prices),
    url(r'^api/create_shipping_address/$', create_shipping_address),
    url(r'^api/create_billing_address/$', create_billing_address),
    url(r'^api/update_order/$', update_order),
    url(r'^api/update_order_cart/$', update_order_cart),
    url(r'^api/update_cart/$', update_cart),
    url(r'^api/remove_order_cart/(?P<pk>[-\w]+)/$', remove_order_cart),
    url(r'^payer/$', PayView.as_view()),
    url(r'^landingpage/login/$', LoginView.as_view()),
    url(r'^landingpage/resume/$', PayResume.as_view()),
    url(r'^landingpage/panier/$', CartResume.as_view()),
    url(r'^landingpage/payer/$', PayView.as_view()),
    url(r'^landingpage/address/create_shipping/$', ShippingCreate.as_view()),
    url(r'^landingpage/address/create_billing/$', BillingCreate.as_view()),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^paid/$', PaidView.as_view()),
    url(r'^success/$', OrderSuccess.as_view()),
    url(r'^cancel/$', TemplateView.as_view(template_name='easycheckout/cancelled_payment.html')),
    url(r'^error/$', TemplateView.as_view(template_name='easycheckout/cancelled_payment.html')),
    url(r'^wait/$', TemplateView.as_view(template_name='easycheckout/wait_payment.html')),
    url(r'^ipn/$', ipn),
    url(r'^(?P<pk>[-\w]+)/$', OrderDetailView.as_view(), name='booking-room-detail'),
]