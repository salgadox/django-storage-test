from django import forms

from django_storage_test.files.models import File


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ["file"]
