from django.test import TestCase
from payment.models import SupplierPaymentTransaction
from supplier.models import Supplier
from _helpers.tests import SUPPLIER, STATUS, SUPPLIER_TRANSACTIONS
from status.models import Status

class SupplierTest(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    
    def test_create_supplier_trasactions(self):
        supplier = Supplier.objects.create(**SUPPLIER)
        SUPPLIER_TRANSACTIONS.update({'supplier': supplier})
        transaction = SupplierPaymentTransaction.objects.create(**SUPPLIER_TRANSACTIONS)
        supplier.transactions.add(transaction)
        self.assertTrue(supplier.transactions.get(id=transaction.id))
