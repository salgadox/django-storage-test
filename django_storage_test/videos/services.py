# Example simplified from here
# https://github.com/HackSoftware/Django-Styleguide-Example/blob/master/styleguide_example/files/services.py

import pathlib
from uuid import uuid4

import boto3
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from django_storage_test.videos.models import File, file_generate_upload_path


def file_generate_name(original_file_name):
    extension = pathlib.Path(original_file_name).suffix

    return f"{uuid4().hex}{extension}"


def file_generate_local_upload_url(*, file_id: str):
    url = reverse("api:files:upload:direct:local", kwargs={"file_id": file_id})
    return f"{settings.APP_DOMAIN}{url}"


def s3_get_client():
    return boto3.client(
        service_name="s3",
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )


def s3_generate_presigned_post(*, file_path: str, file_type: str):
    s3_client = s3_get_client()

    acl = settings.AWS_DEFAULT_ACL
    expires_in = settings.AWS_PRESIGNED_EXPIRY

    presigned_data = s3_client.generate_presigned_post(
        settings.AWS_S3_BUCKET_NAME,
        file_path,
        Fields={"acl": acl, "Content-Type": file_type},
        Conditions=[
            {"acl": acl},
            {"Content-Type": file_type},
        ],
        ExpiresIn=expires_in,
    )
    return presigned_data


class FileDirectUploadService:
    @transaction.atomic
    def start(self, *, file_name: str, file_type: str):
        file = File(
            original_file_name=file_name,
            file_name=file_generate_name(file_name),
            file_type=file_type,
            file=None,
        )
        file.full_clean()
        file.save()

        upload_path = file_generate_upload_path(file, file.file_name)

        """
        We are doing this in order to have an associated file for the field.
        """
        file.file = file.file.field.attr_class(file, file.file.field, upload_path)
        file.save()

        presigned_data = {}

        if settings.FILE_UPLOAD_STORAGE == "s3":
            presigned_data = s3_generate_presigned_post(
                file_path=upload_path, file_type=file.file_type
            )
        else:
            presigned_data = {
                "url": file_generate_local_upload_url(file_id=str(file.id)),
            }

        return {"id": file.id, **presigned_data}

    @transaction.atomic
    def finish(self, *, file: File) -> File:
        file.upload_finished_at = timezone.now()
        file.full_clean()
        file.save()

        return file

    @transaction.atomic
    def upload_local(self, *, file: File, file_obj) -> File:
        file.file = file_obj
        file.full_clean()
        file.save()

        return file
