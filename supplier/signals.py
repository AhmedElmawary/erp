# from django.db.models.signals import pre_save, post_save
# from django.utils.translation import gettext_lazy as _
# from payment.models import SupplierPaymentTransaction, PaymentTransactionType
# from supplier.models import Supplier
# from django.dispatch import receiver, Signal

# @receiver(post_save, sender=Supplier)
# def add_inital_transaction(sender, **kwargs):
#     if kwargs.get('created'):
#         supplier = kwargs['instance']
#         if supplier.cash == 0 :
#             return
        
#         if not SupplierPaymentTransaction.objects.filter(supplier_id=supplier.pk).exists():
#             if supplier.cash < 0:
#                 try:
#                     type_tranasction = PaymentTransactionType.objects.get(name=_('Opening account'))
#                 except PaymentTransactionType.DoesNotExist:
#                     type_tranasction = PaymentTransactionType.objects.create(
#                         name=_('Opening account'),
#                         transaction_for=2
#                     )

#                 SupplierPaymentTransaction.objects.create(
#                     amount=abs(supplier.cash),
#                     supplier=supplier,
#                     type_tranasction=type_tranasction,
#                     payment_type=2,
                    
#                 )
#                 return

#             try:
#                 type_tranasction = PaymentTransactionType.objects.get(name=_('Opening account'))
#             except PaymentTransactionType.DoesNotExist:
#                 type_tranasction = PaymentTransactionType.objects.create(
#                     name=_('Opening account'),
#                     transaction_for=1
#                 )

#             SupplierPaymentTransaction.objects.create(
#                 amount=supplier.cash,
#                 supplier=supplier,
#                 type_tranasction=type_tranasction,
#                 payment_type=1
#             )
