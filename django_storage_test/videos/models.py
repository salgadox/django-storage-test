from django.conf import settings
from django.db import models


def file_generate_upload_path(instance, filename):
    # Both filename and instance.file_name should have the same values
    return f"files/{instance.file_name}"


class File(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=("Uploaded by"),
        editable=False,
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to=file_generate_upload_path)
    original_file_name = models.TextField()
    file_name = models.CharField(max_length=255, unique=True)
    file_type = models.CharField(max_length=255)
    upload_finished_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_valid(self):
        """
        We consider a file "valid" if the the datetime flag has value.
        """
        return bool(self.upload_finished_at)

    @property
    def url(self):
        # if "FileSystemStorage" in settings.DEFAULT_FILE_STORAGE:
        # return f"{settings.APP_DOMAIN}{self.file.url}"
        return self.file.url
