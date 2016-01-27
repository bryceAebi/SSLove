from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

class Love(models.Model):
    sender = models.ForeignKey(
        User,
        related_name='sent_love')

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recieved_love')

    text = models.CharField(max_length=300)
