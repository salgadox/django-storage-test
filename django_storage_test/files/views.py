from django.shortcuts import render
from django.views import View

from .models import File


class FileListView(View):
    def get(self, request, *args, **kwargs):
        files = File.objects.filter(uploaded_by=self.request.user)
        return render(request, "file_list.html", {"files": files})


class FileDetailView(View):
    def get(self, request, *args, **kwargs):
        file = File.objects.get(file_name=kwargs["file_name"])
        return render(request, "file_detail.html", {"file": file})
