from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from users.models import ApprovedEmail

@python_2_unicode_compatible
class Love(models.Model):

    sender = models.ForeignKey(
        ApprovedEmail,
        on_delete=models.CASCADE,
        related_name='sent_love')

    recipient = models.ForeignKey(
        ApprovedEmail,
        on_delete=models.CASCADE,
        related_name='recieved_love')

    text = models.CharField(max_length=300)

    creation_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.sender.email + ' -> ' + self.recipient.email + ':  \"' + self.text + '"'
