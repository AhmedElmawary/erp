from django.utils.translation import gettext as _
from modeltranslation.translator import translator, TranslationOptions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from modeltranslation.admin import TranslationAdmin
from django.contrib import admin


class PermissionTranslationOptions(TranslationOptions):
    fields = (
            _('name'),
            'content_type',
            # 'codename',
        )
        
class ContentTypeTranslationOptions(TranslationOptions):
    pass
    # fields = (
        # 'app_label',
        # 'model'
    # )

class PermissionAdmin(TranslationAdmin):
        fields = (
            _('name'),
            'content_type',
            # 'codename',
        )

    
# translator.register(Permission, PermissionTranslationOptions)
# translator.register(ContentType, ContentTypeTranslationOptions)
# admin.site.register(Permission, PermissionAdmin)
