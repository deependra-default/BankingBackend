from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail

from BankingBackend.constant import USER_CHOICES


class User(AbstractUser):

    email = models.EmailField(_("email address"), unique=True)
    user_type = models.CharField(max_length=2, choices=USER_CHOICES)
    contact_number = models.CharField(max_length=16)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name

    def send_email(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
