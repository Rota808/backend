"""
URL configuration for back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'pizzas', views.PizzaViewSet)
router.register(r'sizes', views.SizeViewSet)
router.register(r'beverages', views.BeverageViewSet)
router.register(r'pizza-prices', views.PizzaPriceViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'store-info', views.StoreInfoViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'payments', views.PaymentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/orders/<int:pk>/create_mercado_pago_preference/', 
         views.OrderViewSet.as_view({'post': 'create_mercado_pago_preference'}),
         name='create-mercado-pago-preference'),
]