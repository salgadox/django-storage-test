from django.views.generic import DetailView, ListView

from django_storage_test.files.models import File


class FileListView(ListView):
    model = File
    template_name = "file_list.html"
    context_object_name = "files"

    def get_queryset(self):
        return File.objects.filter(uploaded_by=self.request.user)


class FileDetailView(DetailView):
    model = File
    template_name = "file_detail.html"
    context_object_name = "file"
    slug_url_kwarg = "file_name"
    slug_field = "file_name"
