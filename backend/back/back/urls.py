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
]