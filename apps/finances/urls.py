from django.urls import path, include

from . import views

app_name = "finances"

stripe_urls = [
    path("", include("djstripe.urls", namespace="djstripe")),
]

urlpatterns = [
    path("stripe/", include(stripe_urls)),
    path("pricing/", views.PricingView.as_view(), name="pricing"),
    path("pricing/<int:price_id>/", views.PricingPaymentMethod.as_view(), name="pricing_payment_method"),
]
