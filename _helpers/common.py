from django.utils.translation import gettext_lazy as _

def make_list_of_lists(queryset, fields=None, excludes=None , methods=[], include=[]):
    transactions_rows = []
    for transaction in queryset:
        transaction_row = []
        for field in fields:
            if field in include:
                transaction_row.append(str(field))
                continue
            if not field in methods:
                value = getattr(transaction, field)
            else:
                method_to_call = getattr(transaction, field)
                value = method_to_call()
            value = '' if not value else value
            transaction_row.append(str(value))
        transactions_rows.append(transaction_row)
    return transactions_rows


def make_one_dimation_list(queryset, fields=None, excludes=None):
    transaction_row = []
    for transaction in queryset:
        for field in fields:
            transaction_row.append(getattr(transaction, field))
    return transaction_row
