from _helpers.tests import SUPPLIER, json_names_to_dic, generate_phone
from supplier.models import Supplier
from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandParser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
import random


class Command(BaseCommand):
    help = "seeds suppliers the db with default admin"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)
    
    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        data = {
            'email':'admin@panel.erp',
            'first':'admin',
            'age': 26,
            'gender':1,
            'last':'panel',
            'password':'123456',
            'phone': '0122222121',
            'country': 'EG',
            'is_staff': True,
            'is_superuser': True
        }

        if get_user_model().objects.filter(email=data['email']).exists():
            return self.stdout.write(self.style.NOTICE('Admin Already exists'))
        get_user_model().objects.create(**data)
        return self.stdout.write(self.style.SUCCESS('Admin Created!'))

