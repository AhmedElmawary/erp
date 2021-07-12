
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)
import random

from django.utils.translation import ugettext_lazy as _
from _helpers.models import user_img_upload_path, COUNTRIES, USER_AGES, GENDERS
from django.utils.html import format_html
from django.urls.base import reverse


REQUIRED_FIELDS = [
    'first',
    'age',
    'gender',
    'last',
    'password',
    'phone',
    'country',
]

USERNAME_FIELD = 'email'

class UserManager(BaseUserManager):
    def __init__(self, *args, **kwargs):
        self.is_validated = False
        super().__init__(*args, **kwargs)

    def _validate(self, obj):
        FIELDS = REQUIRED_FIELDS + [USERNAME_FIELD]
        for col in FIELDS:
            if not obj[col]:
                raise ValueError(f'{col} connot be empty')

        self.is_validated = True

    def create(self, **obj):
        self._validate(obj)
        if not self.is_validated:
            raise ValueError('bad data provided')

        password = obj.pop('password')
        obj['email'] = self.normalize_email(obj['email'])
        user = self.model(**obj)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staff(self, **obj):
        user = self.create(**obj)
        user.is_staff = True
        user.save(using=self._db)

        return user

    def create_superuser(self, **obj):
        user = self.create_staff(**obj)
        user.is_superuser = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _("Users")

    first = models.CharField(
        _('First name'),
        max_length=250,
        blank=False,
    )

    last = models.CharField(
        _('Last name'),
        max_length=250,
        blank=False,
    )

    img = models.ImageField(verbose_name=_(
        'User Image'), blank=True, null=True, upload_to=user_img_upload_path)
    email = models.EmailField(verbose_name=_(
        'User Email'), max_length=250, unique=True, blank=True, null=True)
    phone = models.CharField(verbose_name=_(
        'User Phone Number'),max_length=20, unique=True)

    addtional_phone = models.CharField(verbose_name=_(
        'Addtional User Phone Number'),
        max_length=20, 
        null=True,
        blank=True        
        )

    gender = models.IntegerField(verbose_name=_(
        'Gender'), choices=GENDERS, default=1)
    address = models.CharField(verbose_name=_(
        'User Address'), max_length=250, blank=True, null=True)
    age = models.IntegerField(verbose_name=_(
        'User age'), choices=USER_AGES, default=26)
    city = models.CharField(verbose_name=_('City name'),
                            max_length=250, blank=True, null=True)
    country = models.CharField(verbose_name=_(
        'Country'), choices=COUNTRIES, default="EG", max_length=3)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    is_staff = models.BooleanField(verbose_name=_(
        'Is staff'), default=True, editable=False)
    
    job = models.ForeignKey("Job", verbose_name=_("Job name"), on_delete=models.DO_NOTHING, null=True, blank=True)

    area = models.ForeignKey("area.Area", verbose_name=_("Area"), on_delete=models.DO_NOTHING, null=True, blank=True)
    
    objects = UserManager()

    REQUIRED_FIELDS = REQUIRED_FIELDS

    USERNAME_FIELD = USERNAME_FIELD

    def __str__(self):
        return str(f'{self.first} {self.last}'.capitalize())

    def img_html(self):
        return format_html(
            f'<img src="/media/{self.img}" alt="User Image" width=150px height=150px>'
        )
    img_html.short_description = _("Image preview")

    def get_department(self):
        return  format_html('<p style="padding: 10px; font-weight:bold;" id=job_department;>{}</p>',self.job.department) 
    get_department.short_description = _('Department')


    # def clean_phone(self, *args, **kwargs) -> None:
    #     print(args)
    #     print(kwargs)
    #     if not self.phone.isdigit():
    #         num = random.random() * 45646456
    #         self.addtional_phone = f'0000000000{num}'

    # def clean_additional_phone(self, *args, **kwargs) -> None:
    #     if not self.addtional_phone.isdigit():
    #         num = random.random() * 45646456
    #         self.addtional_phone = f'0000000000{num}'
    
    # def clean_phones(self, *args, **kwargs):
    #     self.clean_additional_phone()
    #     self.clean_phone()

    def clean(self) -> None:
        # self.clean_phones()
        return super().clean()
    
    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)

class Job(models.Model):
    title = models.CharField(_("Job"), max_length=250)
    department = models.ForeignKey("Department", verbose_name=_("Department"), related_name='jobs',on_delete=models.CASCADE)
    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("Job_detail", kwargs={"pk": self.pk})
    
    def __str__(self) -> str:
        return str(self.title)

class Department(models.Model):
    name = models.CharField(_("Name"), max_length=250)
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Department_detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return str(self.name)

class ClosingPeriod(models.Model):
    cash     = models.IntegerField(_("cash"))
    supplier = models.ForeignKey("supplier.Supplier", verbose_name=_("Supplier"), on_delete=models.DO_NOTHING, related_name='peroid', null=True, blank=True)
    client   = models.ForeignKey("client.Client", verbose_name=_("Client"), on_delete=models.DO_NOTHING, related_name='peroid', null=True, blank=True)
    day =  models.DateTimeField(_("date"), auto_now=False, auto_now_add=False)
    delimter = models.CharField(_("delimiter"), max_length=50)
    class Meta:
        verbose_name = _("Closing Period")
        verbose_name_plural = _("Closing Period")

    def __str__(self):
        return str(self.cash)

    def get_absolute_url(self):
        return reverse("ClosingPeriod_detail", kwargs={"pk": self.pk})
