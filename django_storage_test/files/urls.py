from django.urls import path

from django_storage_test.files.views import FileDetailView, FileListView

app_name = "files"
urlpatterns = [
    path("", FileListView.as_view(), name="list"),
    path("<str:file_name>/", FileDetailView.as_view(), name="detail"),
]
