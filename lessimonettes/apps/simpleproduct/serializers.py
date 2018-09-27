from rest_framework import serializers
from .models import Category, Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage


class ProductSerializer(serializers.ModelSerializer):
    get_last_image = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ('id', 'category','is_selected', 'product_type', 'title', 'product_title', 'product_code', 'slug', 'max_number', 'description', 'number', 'temp_number', 'date_availability', 'weight', 'price', 'is_active', 'get_last_image')

