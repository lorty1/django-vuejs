# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from .views import PageList, PageDetail
urlpatterns = [ 
    url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', PageDetail.as_view(), name='PageDetail'),
    url(r'^pages/$', PageList.as_view(), name='PageList'),
]
