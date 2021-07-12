from django.db.models.signals  import pre_save
from django.dispatch import receiver
# from .models import SupplierInvoice


# @receiver(pre_save, sender=Invoice)
# def make_invoice_history(sender, **kwargs):
#     Activity.objects.create(
#         client=sender.client,
#         invoice=sender,
#     )
    