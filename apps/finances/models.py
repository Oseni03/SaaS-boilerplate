from djstripe import models as djstripe_models
from django.urls import reverse

from . import managers


class Product(djstripe_models.Product):
    class Meta:
        proxy = True

    objects = managers.ProductManager()


class Price(djstripe_models.Price):
    class Meta:
        proxy = True

    objects = managers.PriceManager()
    
    def get_absolute_url(self):
        return reverse("finances:pricing_payment_method", kwargs={"price_id": self.id,})