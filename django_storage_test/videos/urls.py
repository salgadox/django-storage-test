from django.urls import path

from django_storage_test.videos.views import upload_form

app_name = "videos"
urlpatterns = [path("upload/", view=upload_form, name="upload_form")]
