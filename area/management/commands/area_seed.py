from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.translation import gettext_lazy as _
from area.models import Area
from _helpers.models import areas_en

class Command(BaseCommand):
    help = _('seeds areas into the database')

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        try:
            for area in areas_en(): 
                Area.objects.create(name=area)
            self.stdout.write(self.style.SUCCESS("Area migrated successfully"), ending='\n')
        except:
            self.stderr.write(self.style.ERROR('Areas couldn\'t be migrated '))
