from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class ApprovedEmail(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=100)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    
    def __str__(self):
        return self.email

    @property
    def vanity(self):
        return self.name.replace(' ', '_')
