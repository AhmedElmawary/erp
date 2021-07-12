from random import shuffle
from django.test import TestCase
from supplier.models import Supplier
from _helpers.tests import SUPPLIER, generate_phone, json_names_to_dic , numbers_generator

class SupplierTest(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    
    def test_create_supplier(self):
        supplier = Supplier.objects.create(**SUPPLIER)
        self.assertEqual(str(supplier), SUPPLIER['name'])

    def test_create_bulk_suppliers(self):
        limit = 100
        names = json_names_to_dic(limit)
        for name in names:
            phone = generate_phone(name)
            data = {'name':name, 'phone': phone}
            SUPPLIER.update(data)
            Supplier.objects.create(**SUPPLIER)
        