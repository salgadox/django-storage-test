from rest_framework import serializers

from django_storage_test.files.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            "file_name",
            "file_type",
            "created_at",
            "url",
        ]
