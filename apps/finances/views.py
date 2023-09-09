from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.generic import TemplateView
from djstripe import models as djstripe_models

from .services import customers
from .models import Price, Product

class PricingView(TemplateView):
    template_name = "finances/pricing.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        prices = Price.objects.prefetch_related("product").all()
        context["monthly"] = prices.filter(recurring__interval="month")
        context["yearly"] = prices.filter(recurring__interval="year")
        return context 


def PricingPayment(LoginRequiredMixin, View):
    
    def get(self, request, price_id, *args, **kwargs):
        price = get_object_or_404(Price, id=price_id)
        context = {
            "price": price
        }
        intent.save(request.user)
        context["form"] = forms.CardForm()
        return render(request, "finances/card.html", context)
    
    def post(self, request, price_id, *args, **kwargs):
        if not price_id:
            price_id = request.POST.get("price_id")
        
        form = CardForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            price = Price.objects.get(id=price_id)
            
            card = {
                "number": cleaned_data["number"],
                "exp_month": cleaned_data["exp_month"],
                "exp_year": cleaned_data["exp_year"],
                "cvc": cleaned_data["cvc"],
                "name": cleaned_data["name"],
                "brand": cleaned_data["brand"],
            }
            try:
                stripe_pm = djstripe_models.PaymentMethod._api_create(
                    "type": "card",
                    "card": card,
                    "billing_details": {
                        "email": request.user.email,
                )
                payment_method = djstripe_models.PaymentMethod.sync_from_stripe_data(stripe_pm)
                
                if cleaned_data["auto"]:
                    (customer, _) = djstripe_models.Customer.get_or_create(request.user)
                    customers.set_default_payment_method(request.user, payment_method)
                    
                    subscr = customer.subscribe(price=price)
                    
                    latest_invoice = djstripe_models.Invoice.get(subscr.latest_invoice)
                    
                    payment_intent = djstripe_models.PaymentIntent.objects.get(id=latest_invoice.payment_intent)
                    payment_intent.update(payment_method=payment_method.id, customer=customer.id)
                else:
                    
                    payment_intent = PaymentIntentForm(data={"price": price})
                    payment_intent.save()
                
                ret = payment_intent._api_confirm(payment_method=payment_method)
                if ret.status == "requires_action":
                    context = {}
                    context["client_secret"] = payment_intent.client_secret
                    context["STRIPE_PUBLISHABLE_KEY"] = settings.STRIPE_PUBLISHABLE_KEY
                    
                    djstripe_models.PaymentIntent.sync_from_stripe_data(payment_intent)
                    
                    return render(request, "finances/3dsec.html", context)
                
                djstripe_models.PaymentIntent.sync_from_stripe_data(payment_intent)
                return render(request, "finances/subscribe.html")
            except Exception as e:
                messages.info(request, e)
        else:
            for error in form.errors.values():
                messages.info(request, error)
        
        context["form"] = form
        return render(request, "finances/card.html", context)