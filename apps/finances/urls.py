from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'prices', views.ProductsViewset,basename="products")
router.register(r'payment-intent', views.PaymentIntentViewset,basename="payment_intent")
router.register(r'subscription-schedule', views.UserSubscriptionScheduleViewset,basename="subscription_schedules")
router.register(r'payment-methods', views.UpdatePaymentMethodView,basename="payment_method")


urlpatterns = [
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path('', include(router.urls)),
]
