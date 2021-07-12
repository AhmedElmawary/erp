
from django import forms
from django.utils.translation import ugettext_lazy as _
from supplier.models import Supplier

class ActionForm(forms.Form):
    comment = forms.CharField(required=False, widget=forms.Textarea, max_length=500)
    
    def form_action(self, supplier):
        raise NotImplementedError()

    def save(self, supplier):
        try:
            supplier, acction = self.form_action(supplier)
        except:
            error_message = str('error')
            self.add_error(None, error_message)
            raise
        
        return supplier, acction

class Withdraw(ActionForm):
    amount = forms.IntegerField(max_value=9999999, min_value=1, required=True, help_text=_("how to withdraw"))

    field_order = (
        'amount',
        'comment'
    )

    def form_action(self, supplier):
        print('WORKSSS')
        return Supplier.objects.get(pk=supplier.id)
