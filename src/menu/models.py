from django.db import models
from django.conf import settings


class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="menu_images/", null=True, blank=True)
    cooking_options = models.CharField(max_length=255, blank=True, help_text="Comma separated cooking options like Rare,Medium,Well")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.category.name}"

class PriceChange(models.Model):
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE, related_name='price_changes')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    old_price = models.DecimalField(max_digits=8, decimal_places=2)
    new_price = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)  # optional short note
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.menu_item.name}: {self.old_price} -> {self.new_price} by {self.changed_by}"