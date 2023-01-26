import mimetypes
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from django_storage_test.files.client import s3_generate_presigned_post
from django_storage_test.files.models import File
from django_storage_test.files.utils import (
    bytes_to_mib,
    file_generate_local_upload_url,
    file_generate_name,
    file_generate_upload_path,
)


def _validate_file_size(file_obj):
    max_size = settings.FILE_MAX_SIZE

    if file_obj.size > max_size:
        raise ValidationError(
            f"File is too large. It should not exceed {bytes_to_mib(max_size)} MiB"
        )


class FileStandardUploadService:
    """
    This also serves as an example of a service class,
    which encapsulates 2 different behaviors (create & update) under a namespace.

    Meaning, we use the class here for:

    1. The namespace
    2. The ability to reuse `_infer_file_name_and_type` (which can also be an util)
    """

    def __init__(self, user=None, file_obj=None):
        self.user = user
        self.file_obj = file_obj

    def _infer_file_name_and_type(
        self, file_name: str = "", file_type: str = ""
    ) -> tuple[str, str]:
        if not file_name:
            file_name = self.file_obj.name

        if not file_type:
            guessed_file_type, encoding = mimetypes.guess_type(file_name)

            if guessed_file_type is None:
                file_type = ""
            else:
                file_type = guessed_file_type

        return file_name, file_type

    @transaction.atomic
    def create(self, file_name: str = "", file_type: str = "") -> File:
        _validate_file_size(self.file_obj)

        file_name, file_type = self._infer_file_name_and_type(file_name, file_type)

        obj = File(
            file=self.file_obj,
            original_file_name=file_name,
            file_name=file_generate_name(file_name),
            file_type=file_type,
            uploaded_by=self.user,
            upload_finished_at=timezone.now(),
        )

        obj.full_clean()
        obj.save()

        return obj

    @transaction.atomic
    def update(self, file: File, file_name: str = "", file_type: str = "") -> File:
        _validate_file_size(self.file_obj)

        file_name, file_type = self._infer_file_name_and_type(file_name, file_type)

        file.file = self.file_obj
        file.original_file_name = file_name
        file.file_name = file_generate_name(file_name)
        file.file_type = file_type
        file.uploaded_by = self.user
        file.upload_finished_at = timezone.now()

        file.full_clean()
        file.save()

        return file


class FileDirectUploadService:
    """
    This also serves as an example of a service class,
    which encapsulates a flow (start & finish) + one-off action (upload_local) into a namespace.

    Meaning, we use the class here for:

    1. The namespace
    """

    def __init__(self, user):
        self.user = user

    @transaction.atomic
    def start(self, *, file_name: str, file_type: str) -> dict[str, Any]:
        file = File(
            original_file_name=file_name,
            file_name=file_generate_name(file_name),
            file_type=file_type,
            uploaded_by=self.user,
            file=None,
        )
        file.full_clean()
        file.save()
        # TODO fix ugly hardcoded media
        upload_path = file_generate_upload_path(file, file.file_name)

        """
        We are doing this in order to have an associated file for the field.
        """
        file.file = file.file.field.attr_class(file, file.file.field, upload_path)
        file.save()
        # upload_path = file.file.name
        presigned_data: dict[str, Any] = {}
        # TODO fixhardcoded media path
        if "S3" in settings.DEFAULT_FILE_STORAGE:
            presigned_data = s3_generate_presigned_post(
                file_path="media/" + upload_path, file_type=file.file_type
            )

        else:
            presigned_data = {
                "url": file_generate_local_upload_url(file_id=str(file.id)),
            }

        return {"id": file.id, **presigned_data}

    @transaction.atomic
    def finish(self, *, file: File) -> File:
        # Potentially, check against user
        file.upload_finished_at = timezone.now()
        file.full_clean()
        file.save()

        return file

    @transaction.atomic
    def upload_local(self, *, file: File, file_obj) -> File:
        _validate_file_size(file_obj)

        # Potentially, check against user
        file.file = file_obj
        file.full_clean()
        file.save()

        return file
