from django.db.models.fields.related import ManyToManyField
from django.forms.models import ModelMultipleChoiceField
from _helpers.models import areas_ar_en, areas_en
from typing import Any, List, Optional, Sequence, Tuple
from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin, ModelAdmin, TabularInline
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.messages.constants import ERROR
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls.resolvers import URLPattern
from django.utils.translation import gettext, gettext_lazy, ugettext as _, ugettext_lazy
from rest_framework.authtoken import admin as rest_admin
from django.contrib.auth.models import Group, Permission
from django.utils.html import format_html
from app_user.models import Department, Job, User
from area.models import Area
from django.contrib import messages
from django.urls import path

class NoDeletion(admin.ModelAdmin):
    def has_delete_permission(self, request: HttpRequest, obj: Optional["Model"]=None) -> bool:
        return False
    
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    area = forms.ModelChoiceField(queryset=Area.objects.all(), required=False, label=ugettext_lazy("Area"))
    password1 = forms.CharField(label=ugettext_lazy("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=ugettext_lazy("Password confirmation"),
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email", "last", "first", 'area')

    def clean_password2(self):
        
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
        the user, but replaces the password field with admin's
            password hash display field.
    
    """
    # password = ReadOnlyPasswordHashField(label=_('Password')) 
    new_password      = forms.CharField(strip=False, widget=forms.PasswordInput(),label=_("New password"), error_messages={'confirm_password': _('passwords don\'t match')}, required=False)
    confirm_password  = forms.CharField(strip=False, widget=forms.PasswordInput(),label=_("Confirm new password"), error_messages={'confirm_password': _('passwords don\'t match')}, required=False)
  
    class Meta:
        model = User
        fields = (
            _('new_password'),
            _('confirm_password'),
            )

    def clean_password(self):
        password1 = self.cleaned_data.get("new_password")
        password2 = self.cleaned_data.get("confirm_password")
        
        if password1 and password2 and password1 != password2:
            # self.add_error('new_password', ValidationError("Passwords don't match"))
            return
        return password2
    
    def save(self, commit=True) -> None:
        password = self.clean_password() 
        if  password:
            self.instance.set_password(password)
        return super().save(commit)


class CustomUserAdmin(UserAdmin):
    class Media: 
        js = ('dynamic_department.js',)

    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("id", "email",  "phone", "gender", "is_active", "last_login", 'area')

    list_display_links = ("email",)
    list_filter = ("last_login", "is_active", "gender")
    ordering = ("-id",)
    list_per_page = 15
    readonly_fields = ('id', "last_login", 'img_html', 'is_staff', 'get_department')

    search_fields = [
        'country',
        'email',
        'phone',
        'area__name'
    ]

    actions = [_('activate'), _('deactivate'), ]

    def get_search_results(self, request: HttpRequest, queryset: QuerySet, search_term: str) -> Tuple[QuerySet, bool]:
        areas_ar_en_data = areas_ar_en()
        for value in areas_ar_en_data :
            value_en = value.get(search_term)
            if value_en:
                search_term = value_en 
        return super().get_search_results(request, queryset, search_term)
    
    def activate(self, request, queryset):
        count= queryset.update(is_active=True)
        users_string = 'users' if count < 1 else 'user'
        self.message_user(request, f'{count} {users_string} activated successfully')

    activate.short_description = ugettext_lazy('Activate users')


    def deactivate(self, request, queryset):
        count= queryset.update(is_active=False)
        users_string = 'users' if count < 1 else 'user'
        self.message_user(request, f'{count} {users_string} deactivated successfully')
    deactivate.short_description = ugettext_lazy('Deactivate users')

    def has_delete_permission(self, request, obj=None):
        return False
    

    def get_urls(self) -> List[URLPattern]:
        urls =  super().get_urls()
        return urls + [
            path('<int:user_id>/job/<int:job_id>', self.get_department_ajax, name='job-department') 
        ]


    def get_department_ajax(self, request, user_id,job_id):
        response = str(self.get_object(request, user_id).job.department)

        department = Department.objects.filter(jobs=job_id)
        if department.exists():
            department = department.get()
            response = str(department)

        return  JsonResponse({'department': response} , status=200)
        
    def response_add(self, request, obj, post_url_continue=None):
        from django.urls.base import reverse
        """
        This makes the response after adding go to another 
        app's changelist for some model
        """
        return HttpResponseRedirect(
            reverse("admin:app_user_user_changelist")
        )

    fieldsets = (
        (ugettext_lazy("Login"), {
            'classes': ('collapse', "wide"),
            "fields": (
                _('id'),
            "email",  
            "last_login"
            )
            }),
        (_('Change Password'), {
            'classes': ('collapse', 'wide'),
            'fields':
            (
            _('new_password'),
            _('confirm_password')
            ),
        }),
        (ugettext_lazy("Personal_info"),{
                'classes': ("wide",),
                "fields": (
                    ("img", "img_html"),
                    ("first", "last", 'phone', 'addtional_phone'),
                    ('job', 'get_department'),
                    ("gender",'age'),
                    ("country", 'area', 'city', 'address')
                )
            },
        ),
        (
            ugettext_lazy("Important Dates"),
            {

                'classes': ('collapse', "wide"),
                "fields": (_("is_active"), _("is_staff"), _("is_superuser"))},
        ),
        (ugettext_lazy("Permissions"), {
            'classes': ('collapse', "wide"),
            "fields": ("groups",)}),
            # "fields": ("user_permissions", "groups")}),
    )
    
    add_fieldsets = (
            (gettext_lazy('login'),{"classes": ('wide',) , 'fields': ('email', 'password1', 'password2')},),
            (gettext_lazy('user name'),{"classes": ('wide',) , 'fields': (('first', 'last',), )},),
            (gettext_lazy('user location'),{"classes": ('wide',) , 'fields': (('area', 'country'),),}),
            (gettext_lazy('general'),{"classes": ('wide',) , 'fields': ('job','img', ('gender', 'age'), ('phone', 'addtional_phone'))}),
            (gettext_lazy('Permissinos'),{"classes": ('wide',) , 'fields': ('groups',)}),
    )   

class JobAdmin(NoDeletion):
    pass

class DepartmanAdmin(NoDeletion):
    pass

admin.site.register(User, CustomUserAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Department, DepartmanAdmin)
admin.site.unregister(rest_admin.TokenProxy)

admin.site.index_title = _('ERP APP')
admin.site.site_header = _('ERP APP Administration')
admin.site.site_title = _('ERP APP Management')



from django.contrib.auth.models import Group, Permission


class GroupAdmin(ModelAdmin):
    
    
    filter_vertical = ('permissions', )
    def formfield_for_manytomany(self, db_field: ManyToManyField, request: Optional[HttpRequest], **kwargs: Any) -> ModelMultipleChoiceField:
        excludes = [
            'contenttype',
            'session',
            'logentry',
            'token',
            'tokenproxy',
            'ctx',
            'vat'
            ]
        kwargs['queryset'] = Permission.objects.exclude(content_type__model__in=excludes)
        
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)