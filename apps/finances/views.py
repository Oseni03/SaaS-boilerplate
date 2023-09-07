from django.conf import settings


from .models import Price, Product

class PricingView(TemplateView):
    template_name = "finances/pricing.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        prices = Price.objects.prefetch_related("product").all()
        context["monthly"] = prices.filter(recurring.interval="month")
        context["yearly"] = prices.filter(recurring.interval="year")
        return context 


def PricingPaymentMethod(LoginRequiredMixin, View):
    
    def get(self, request, price_id, *args, **kwargs):
        price = Price.objects.get(id=price_id)
        context = {
            "price": price
        }
        intent = PaymentIntentForm(data={"price": price})
        intent.save(request.user)
        context["client_secret"] = intent.client_secret
        context["payment_intent_id"] = intent.id
        context["STRIPE_PUBLISHABLE_KEY"] = settings.STRIPE_PUBLISHABLE_KEY
        return render(request, "finances/card.html", context)
    
    def post(self, request, *args, **kwargs):
        payment_intent_id = request.POST.get("payment_intent_id")
        payment_method_id = request.POST.get("payment_method_id")
        
        stripe.PaymentIntent.modify(
            payment_intent_id,
            payment_method=payment_method_id
        )
        
        stripe.PaymentIntent.confirm(payment_method_id)
        return render(request, "finances/payment_successful.html")