from django.db.models.signals import post_save
from django.core.signals import Signal
from django.dispatch import receiver
from django.core.mail import (
    EmailMessage,
    EmailMultiAlternatives
    )

from django.template.loader import render_to_string

from app_user.models import User


@receiver(post_save, sender=User)
def send_welcome_email(sender, **kwargs):
    template = render_to_string(
        'emails/app_user/welcome.html',
        context={ "user" : kwargs['instance'] },
    )

    email = EmailMessage(
        subject='We are happy to have you with us!',
        body=template
    )

    email.content_subtype= 'html'
    # email.attach('design.png', img_data, 'image/png')
    # email.attach_file('attachment/erplast.pdf')
    # email.attach_file('attachment/1.jpeg')
    # email.attach_file('attachment/1.jpg')
    email.send(fail_silently=False)