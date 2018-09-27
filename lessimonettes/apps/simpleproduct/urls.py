# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [ 
    url('^$',
        views.ProductCategories.as_view(),
        name='product-list'
        ),
    url('^nouveau/',
        views.NewBox.as_view(),
        name='new-box'
    ),
    url('^detail/(?P<slug>.*)/',
        views.ProductDetail.as_view(),
        name='product-detail'
    ),
    url('^rest/product/liste-boites/',
        views.ListBoitesProducts.as_view(),
        name='product-list-boite'
    ),
    url('^rest/product/liste-cookies/',
        views.ListCookiesProducts.as_view(),
        name='product-list-cookies'
    ),
   url('^rest/product/(?P<pk>.*)/',
        views.get_product,
        name='product-category-detail'
    ),
    url('^(?P<category>.*)/',
        views.ProductCategoryDetails.as_view(),
        name='product-category-list'
    ),
]
