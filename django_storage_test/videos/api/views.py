from django.core.files.storage import default_storage
from rest_framework import status, viewsets
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_storage_test.videos.models import Video

from .serializers import VideoSerializer


class VideoViewSet(viewsets.ModelViewSet):
    parser_classes = (FileUploadParser,)
    permission_classes = (IsAuthenticated,)
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        video_file = request.FILES["video"]
        # generate pre-signed URL for uploading the file
        # url = default_storage.url(video_file.name)
        # upload the file
        with open(video_file.temporary_file_path(), "rb") as src:
            default_storage.save(video_file.name, src)
        # create the Video object and save it to the database
        # video_data = request.data.copy()
        # video_data["user"] = self.request.user
        serializer = self.get_serializer(
            data=request.data, context={"video_file": video_file}
        )
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            # headers = self.get_success_headers(serializer.data)
            return Response(
                "ok"
                # serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def list(self, request, *args, **kwargs):
    queryset = self.filter_queryset(self.get_queryset())
    serializer = VideoSerializer(queryset, many=True)
    return Response(serializer.data)
