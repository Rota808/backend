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
    path('api/payments/webhook/', views.OrderViewSet.as_view({'post': 'mercadopago_webhook'}), name='mercadopago-webhook'),
    # New endpoint for confirming payments on client-side
    path('api/payments/<int:pk>/confirm/',
         views.OrderViewSet.as_view({'post': 'confirm_payment'}),
         name='confirm-payment'),
]