from _helpers.tests import SUPPLIER, json_names_to_dic, generate_phone
from supplier.models import Supplier
from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandParser
from django.utils.translation import ugettext_lazy as _
import random


class Command(BaseCommand):
    help = "seeds suppliers the db with data"

    def add_arguments(self, parser: CommandParser) -> None:
        # Positional arguments
        parser.add_argument('num', type=int)
        # Named arguments
        # parser.add_argument(
        #     '--create',
        #     action='store_true',
        #     help='Create suppliers',
        #     type=int
        #     )

        return super().add_arguments(parser)
    
    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        num  = self._validate_num(options['num'])
        self._create_limit(num)
        self.stdout.write(self.style.MIGRATE_HEADING(f'migrating {num} supplier'))
        self.stdout.write(self.style.SUCCESS('Data has migrated successfully')) 

    def _validate_num(self, num):
        if num > 1000 or num < 1:
            num = 1000
        return num
    
    def _create_limit(self, num):
        names_file = json_names_to_dic()
        names = json_names_to_dic(num)
        for row in range(num):
            name = names[row]
            phone  = generate_phone(name)
            data = {
                'name': name,
                'phone': phone
            }
            SUPPLIER.update(data)
            Supplier.objects.create(**SUPPLIER)