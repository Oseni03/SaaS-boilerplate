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


def PricingPaymentMethod(View):
    
    def get(self, request, price_id, *args, **kwargs):
        context = {
            "price": Price.objects.prefetch_related("product").get(id=price_id)
        }
        intent = PaymentIntentForm(data={"price": price})
        intent.save(request.user)
        context["client_secret"] = intent.client_secret
        context["STRIPE_PUBLISHABLE_KEY"] = settings.STRIPE_PUBLISHABLE_KEY
        return render(request, "finances/card.html", context)
    
    def post(self, request, id, *args, **kwargs):
        pass
        
        