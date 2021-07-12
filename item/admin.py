from django.contrib import admin
from .models import (
    Item,
    Status,
    Category,
    Variation,
    Discount,
    Option,
    Vat,
    # CTX
    )

class CannotDelete(admin.ModelAdmin):
    def has_delete_permission(self, *args, **kwargs):
        return False

class ItemAdmin(CannotDelete):
    autocomplete_fields = ['variation']
    search_fields = [
        'name',
        'label',
        'price',
        'supplier_price'
    ]

class CategoryAdmin(CannotDelete):
    def get_model_perms(self, request): return {}

    search_fields = [
        'name'
    ]

class StatusAdmin(CannotDelete):
    def get_model_perms(self, request): return {}
    
    search_fields = [
        'name'
    ]


class VariationAdmin(CannotDelete):
    def get_model_perms(self, request): return {}
    
    autocomplete_fields = ['category', 'option']
    search_fields = [
        'category',
    ]

class DiscountAdmin(CannotDelete):
    def get_model_perms(self, request): return {}
    search_fields = [
        'amount',
        # 'option'
    ]


class VatAdmin(CannotDelete):
    def get_model_perms(self, request): return {}


class CTXAdmin(CannotDelete):
    def get_model_perms(self, request): return {}




class OptionAdmin(CannotDelete):
    def get_model_perms(self, request): return {}

    search_fields = [
        'title'
    ]


admin.site.register(Item, ItemAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(Discount, DiscountAdmin)
# admin.site.register(Vat, VatAdmin)
# admin.site.register(CTX, CTXAdmin)
admin.site.register(Option, OptionAdmin)