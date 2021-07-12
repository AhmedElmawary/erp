from django.contrib import admin
from django.utils.translation import gettext_lazy
from payment.models import PaymentTransactionType

class ClientTransactionType(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = gettext_lazy('Transaction type')

    # Parameter for the filter that will be used in the URL query.
    # parameter_name = 'type_tranasction__id__exact'
    parameter_name = 'transactions_type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        options_for_client = []
        for row in PaymentTransactionType.objects.filter(for_client=True):
            options_for_client.append((row.id, str(row)))
        return options_for_client

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(type_tranasction=self.value())



class SupplierTransactionType(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = gettext_lazy('Transaction type')

    # Parameter for the filter that will be used in the URL query.
    # parameter_name = 'type_tranasction__id__exact'
    parameter_name = 'transactions_type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        options_for_supplier = []
        for row in PaymentTransactionType.objects.filter(for_supplier=True):
            options_for_supplier.append((row.id, str(row)))
        return options_for_supplier

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(type_tranasction=self.value())
