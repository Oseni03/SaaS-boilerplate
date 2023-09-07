from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.generic import TemplateView
from djstripe import models as djstripe_models


from .models import Price, Product

class PricingView(TemplateView):
    template_name = "finances/pricing.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        prices = Price.objects.prefetch_related("product").all()
        context["monthly"] = prices.filter(recurring__interval="month")
        context["yearly"] = prices.filter(recurring__interval="year")
        return context 


def PricingPaymentMethod(LoginRequiredMixin, View):
    
    def get(self, request, price_id, *args, **kwargs):
        price = get_object_or_404(Price, id=price_id)
        context = {
            "price": price
        }
        intent = PaymentIntentForm(data={"price": price})
        intent.save(request.user)
        context["payment_intent_id"] = intent.id
        context["form"] = forms.CardForm()
        return render(request, "finances/card.html", context)
    
    def post(self, request, *args, **kwargs):
        payment_intent_id = request.POST.get("payment_intent_id")
        payment_intent = djstripe_models.PaymentIntent.objects.get(id=payment_intent_id)
        
        form = CardForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            card = {
                "number": cleaned_data["number"],
                "exp_month": cleaned_data["exp_month"],
                "exp_year": cleaned_data["exp_year"],
                "cvc": cleaned_data["cvc"],
                "name": cleaned_data["name"],
                "brand": cleaned_data["brand"],
            }
            try:
                card_token = djstripe_models.create_token(
                    cleaned_data["number"],
                    cleaned_data["exp_month"],
                    cleaned_data["exp_year"],
                    cleaned_data["cvc"],
                    name=cleaned_data["name"],
                    brand=cleaned_data["brand"],
                )
                
                payment_method = forms.PaymentMethodForm(data={
                    "type": "card",
                    "card": card,
                    "billing_details": {
                        "email": request.user.email,
                    }
                })
                payment_method.save()
                
                payment_intent.update({
                    "payment_method": payment_method
                })
                
                payment_intent._api_confirm(payment_method=payment_method)
                djstripe_models.PaymentIntent.sync_from_stripe_data(payment_intent)
                return render(request, "finances/subscription.html")
            except Exception as e:
                messages.info(request, e)
        else:
            for error in form.errors.values():
                messages.info(request, error)
        
        context["payment_intent_id"] = payment_intent_id
        context["form"] = form
        return render(request, "finances/card.html", context)