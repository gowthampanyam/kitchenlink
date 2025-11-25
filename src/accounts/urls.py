from django.urls import path
from .views import CreateUserView, LoginView

urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('login/', LoginView.as_view(), name='login'),
]
