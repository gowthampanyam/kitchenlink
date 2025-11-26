from rest_framework import serializers
from .models import MenuItem, MenuCategory, PriceChange

class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'description']


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=MenuCategory.objects.all())
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'category', 'name', 'description', 'price', 'available', 'image', 'image_url', 'cooking_options', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return None

class PriceChangeSerializer(serializers.Serializer):
    new_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate_new_price(self, value):
        # Ensure price is not negative
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value