from django.conf import settings
from django.db import models


class Video(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=("Uploaded by"),
        editable=False,
        on_delete=models.CASCADE,
    )
    video = models.FileField(upload_to="videos/")
