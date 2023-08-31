from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import action

from djstripe import models as djstripe_models

from . import models
from .serializers import (
    PaymentIntentSerializer, 
    SubscriptionItemProductSerializer, 
    CancelUserActiveSubscriptionSerializer,
    UpdateDefaultPaymentMethodSerializer,
    UserSubscriptionScheduleSerializer,
    SubscriptionSerializer,
)

class ProductsViewset(
    viewsets.GenericViewSet, 
    mixins.ListModelMixin
):
    serializer_class = SubscriptionItemProductSerializer
    queryset = models.Product.objects.prefetch_related("prices").filter(prices__active=True)


class SubscriptionViewset(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin, 
    mixins.UpdateModelMixin, 
    mixins.RetrieveModelMixin
):
    serializer_class = SubscriptionSerializer
    
    def get_object(self, request):
        (customer, _) = djstripe_models.Customer.get_or_create(request.user)
        return djstripe_models.Subscription.objects.get(customer=customer)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentIntentViewset(
    mixins.CreateModelMixin, 
    mixins.UpdateModelMixin, 
    viewsets.GenericViewSet
):
    """
    A viewset that provides `create`, and `update` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    serializer_class = PaymentIntentSerializer 
    
    def get_queryset(self, request):
        (customer, _) = djstripe_models.Customer.get_or_create(request.user)
        return djstripe_models.PaymentIntent.objects.filter(customer=customer)
    
    def create(self, request, *args, **kwargs):
        """
        Receives the price id for charge for and subscribe to
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class UserSubscriptionScheduleViewset(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    serializer_class = UserSubscriptionScheduleSerializer
    
    def get_queryset(self, request):
        (customer, _) = djstripe_models.Customer.get_or_create(request.user)
        return djstripe_models.SubscriptionSchedule.objects.filter(customer=customer)
    
    @action(detail=True, methods=['put'], serializer_class=CancelUserActiveSubscriptionSerializer)
    def cancel_subscription(self, request, pk=None):
        subscriptionschedule = self.get_queryset().get(id=pk)
        serializer = CancelUserActiveSubscriptionSerializer(subscriptionschedule)
        serializer.update(subscriptionschedule)
        return Response(serializer.data)


class UpdatePaymentMethodView(
    viewsets.GenericViewSet, 
    mixins.UpdateModelMixin
):
    serializer_class = UpdateDefaultPaymentMethodSerializer
    
    def get_queryset(self, request):
        (customer, _) = djstripe_models.Customer.get_or_create(request.user)
        return djstripe_models.PaymentMethod.objects.filter(customer=customer)

