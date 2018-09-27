# -*- coding: utf-8 -*-

from django.views import generic
from django.views.generic import DetailView, TemplateView
from .models import Category, Product, ProductImage
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from decimal import *


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class ListBoitesProducts(APIView):
    """
    View to list all boxes in the system.
    """

    def get(self, request, format=None):
        """
        Return a list of all boxes.
        """
        products = [product for product in Product.objects.filter(product_type__slug="boite")]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ListCookiesProducts(APIView):
    """
    View to list all cookies in the system.

    """

    def get(self, request, format=None):
        """
        Return a list of all cookies.
        """

        products = [product for product in Product.objects.filter(product_type__slug="cookie")]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductCategories(generic.list.ListView):
    model = Product
    template_name = "simpleproduct/product_categories.html"

    def get_context_data(self, **kwargs):
        context = super(ProductCategories, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        return context

class ProductCategoryDetails(generic.list.ListView):
    model = Product
    template_name = "simpleproduct/product_list.html"

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryDetails, self).get_context_data(**kwargs)
        #context['object_list'] = Product.objects.all()
        context['category'] = Category.objects.get(slug=self.kwargs['category'])
        context['product_list'] = Product.objects.filter(is_active=True).filter(category__slug=self.kwargs['category']).filter(product_type__slug="boite")
        context['cookie_list'] = Product.objects.filter(is_active=True).filter(category__slug=self.kwargs['category']).filter(product_type__slug="cookie")
        return context


class NewBox(TemplateView):
    """Display product with a given slug."""
    template_name = "simpleproduct/new_box.html"

    def get_context_data(self, **kwargs):
        context = super(NewBox, self).get_context_data(**kwargs)
        return context

class ProductDetail(TemplateView):
    """Display product with a given slug."""
    template_name = "simpleproduct/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['product'] = Product.objects.get(slug=self.kwargs['slug'])
        return context

def get_product(self, pk):
    """ Show product
        Arguments:
            pk (int)
        Returns:
            A JSON response with the list.
        Example:
            >>> get_product(3)
            {"hours":"Closed doors"}
    """
    product = Product.objects.get(pk=pk)
        
    return JsonResponse({"title":product.title, \
                         "description":product.description, \
                         "weight":product.weight, \
                         "dlc":product.date_consumption, \
                         "stock_availability":product.date_availability, \
                         "number":product.temp_number, \
                         "image":product.get_last_image(), \
                         "price_kilo":product.price, \
                         "price":"{0:.2f}".format(Decimal(product.price) * Decimal(product.weight) / Decimal(1000)) })
