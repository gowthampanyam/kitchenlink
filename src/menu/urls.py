from django.urls import path
from .views import CreateMenuItemView, ToggleMenuItemAvailability, GetAllCategories, GetAllMenuItems, ChangeMenuItemPrice

urlpatterns = [
    path('items/', CreateMenuItemView.as_view(), name='create-menu-item'),
    path('items/<int:pk>/toggle-available/', ToggleMenuItemAvailability.as_view(), name='toggle-menu-item'),
    path('categories/', GetAllCategories.as_view(), name='get-all-categories'),
    path('items/all/', GetAllMenuItems.as_view(), name='get-all-menu-items'),
    path('items/<int:pk>/change-price/', ChangeMenuItemPrice.as_view(), name='change-menu-item-price'),
]
