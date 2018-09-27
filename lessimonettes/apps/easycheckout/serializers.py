#!/usr/local/bin/python
# coding: utf-8

from rest_framework import serializers
from .models import Order, OrderCart, ItemCart, ShippingAddress, BillingAddress

class ShippingAddressSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return ShippingAddress.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.user = validated_data.get('user', instance.user)
        instance.name = validated_data.get('name', instance.name)
        instance.address1 = validated_data.get('address1', instance.address1)
        instance.address2 = validated_data.get('address2', instance.address2)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.save()
        return instance

    class Meta:
        model = ShippingAddress
        fields = '__all__'

class BillingAddressSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return BillingAddress.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.user = validated_data.get('user', instance.user)
        instance.name = validated_data.get('name', instance.name)
        instance.address1 = validated_data.get('address1', instance.address1)
        instance.address2 = validated_data.get('address2', instance.address2)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.save()
        return instance

    class Meta:
        model = BillingAddress
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCart
        fields = '__all__'

class ItemCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCart
        fields = '__all__'

