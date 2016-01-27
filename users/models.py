from __future__ import unicode_literals

from django.conf import settings
from django.db import models


class ApprovedEmail(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=100)
