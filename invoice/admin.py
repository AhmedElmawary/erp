# from django.contrib import admin
# from django.contrib.admin.options import StackedInline, TabularInline
# from django.db import models
# from django.db.models.fields import files
# from .models import (
#     Order,
#     SupplierInvoice,
#     ClientInvoice,
#     SupplierOrder,
#     ClientOrder
#     )

# from django.utils.translation import ugettext as _
# from item.models import Item
# class ItemInline(TabularInline):
#     def has_change_permission(self, *args, **kwargs) -> bool:
#         return super().has_change_permission(*args, **kwargs)

#     extra = 1
#     verbose_name = _('Item')
#     verbose_name_plural = _('Items')

#     fields = [
#         'item',
#         'quantity',
#         'price',
#         'discount',
#         'cost_per_item'
#     ]

#     readonly_fields = [
#         'cost_per_item_supplier',
#         'cost_per_item',
#     ]
        
#     def has_delete_permission(self, *args, **kwargs) -> bool:
#         return super().has_delete_permission(*args, **kwargs)


# class ClientItemInline(ItemInline):
#     model = ClientOrder.items.through
#     class Media:
#         js = ('client_dynamic_prices.js',)


# class SupplierItemInline(ItemInline):
#     model = SupplierOrder.items.through
#     class Media:
#         js = ('supplier_dynamic_prices.js',)

#     fields = [
#         'item',
#         'quantity',
#         'supplier_price',
#         'discount',
#         'cost_per_item'
#     ]

# class OrderAdmin(admin.ModelAdmin):
#     def has_delete_permission(self, *args, **kwargs) -> bool:
#         return False
    
#     autocomplete_fields = [
#         'status',
#         'payment',
#         'discount',
#         'items',
#     ]

#     readonly_fields = [
#         'cost'
#     ]

#     exclude = (
#         'items',
#     )

# class ClientOrderAdmin(OrderAdmin):
#     inlines = [
#         ClientItemInline
#     ]

#     list_display = ['id','client','status', 'items_cost']
#     autocomplete_fields = ['invoice']
#     list_editable = []
#     empty_value_display = 0    

# class SupplierOrderAdmin(OrderAdmin):
#     inlines = [
#         SupplierItemInline
#     ]


# class InvoiceAdmin(admin.ModelAdmin):
#     class Media:
#         js = (
#             'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js', # jquery
#             'invoice_admin.js', #customjs
#             )

#     # fields = [
#     #     'issued_at',
#     #     'fully_paid',
#     # ]
    
#     def has_delete_permission(self, request, obj=None):
#         return False
#     empty_value_display = 0

#     list_display = ('id', 'issued_at', 'fully_paid', )
#     list_per_page = 15
#     search_fields = (
#         'id',    
#         'fully_paid',
#         'item__name',
#         )

#     list_editable = (
#         'fully_paid',
#     )

# class SupplierInvoiceAdmin(InvoiceAdmin):
#     autocomplete_fields = ['supplier']


# class ClientInvoiceOrder(TabularInline):
#     model = ClientOrder
#     extra = 0

#     fields = [
#         'id',
#         'items_names_html',
#         'items_cost',
#         'payment_method'
#     ]

#     readonly_fields = [
#         'id',
#         'items_names_html',
#         'items_cost',
#         'payment_method'
#     ]
        
#     can_add     = False
#     can_change  = False
#     can_delete  = False

# class ClientInvoiceAdmin(InvoiceAdmin):
#     inlines = [
#         ClientInvoiceOrder,
#     ]

#     autocomplete_fields  = [
#         'client',
#         'status',
#     ]

#     readonly_fields = [
#         'required_money',
#     ]

#     def save_model(self, request, obj, form, change):
#         print('saved')
#         super().save_model(request, obj, form, change)

#     empty_value_display = 0.0


# admin.site.register(SupplierInvoice, SupplierInvoiceAdmin)
# admin.site.register(ClientInvoice, ClientInvoiceAdmin)
# admin.site.register(SupplierOrder, SupplierOrderAdmin)
# admin.site.register(ClientOrder, ClientOrderAdmin)