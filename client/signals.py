from datetime import time
from django.db.models.signals import pre_save, post_save
from django.utils.translation import gettext_lazy as _
from payment.models import ClientPaymentTransaction, PaymentTransactionType
from client.models import Client
from django.dispatch import receiver, Signal
from django.utils import timezone

@receiver(post_save, sender=Client)
def add_inital_transaction(sender, **kwargs):
    if kwargs.get('created'):
        client = kwargs['instance']
        if client.cash == 0 :
            return
        
        if not ClientPaymentTransaction.objects.filter(client_id=client.pk).exists():
            if client.cash < 0:
                try:
                    type_tranasction = PaymentTransactionType.objects.get(name=_('Opening account'))
                except PaymentTransactionType.DoesNotExist:
                    type_tranasction = PaymentTransactionType.objects.create(
                        name=_('Opening account'),
                        transaction_for=2
                    )

                ClientPaymentTransaction.objects.create(
                    amount=abs(client.cash),
                    client=client,
                    type_tranasction=type_tranasction,
                    payment_type=2,
                )
                return

            try:
                type_tranasction = PaymentTransactionType.objects.get(name=_('Opening account'))
            except PaymentTransactionType.DoesNotExist:
                type_tranasction = PaymentTransactionType.objects.create(
                    name=_('Opening account'),
                    transaction_for=1
                )

            ClientPaymentTransaction.objects.create(
                amount=client.cash,
                client=client,
                type_tranasction=type_tranasction,
                payment_type=1
            )
