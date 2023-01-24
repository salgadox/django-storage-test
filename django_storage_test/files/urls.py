from django.urls import path
from django.views.generic import TemplateView

from django_storage_test.files.views import FileDetailView, FileListView

app_name = "files"
urlpatterns = [
    path("", FileListView.as_view(), name="list"),
    path(
        "upload/", TemplateView.as_view(template_name="file_upload.html"), name="upload"
    ),
    path("<str:file_name>/", FileDetailView.as_view(), name="detail"),
]
