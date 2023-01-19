from django.shortcuts import get_object_or_404
# from django.core.files.storage import default_storage
from rest_framework import serializers, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_storage_test.videos.models import File

from .serializers import VideoSerializer

# class VideoViewSet(viewsets.ModelViewSet):
#     parser_classes = (MultiPartParser,)
#     permission_classes = (IsAuthenticated,)
#     queryset = Video.objects.all()
#     serializer_class = VideoSerializer

#     def get_queryset(self):
#         return self.queryset.filter(user=self.request.user)

#     def create(self, request, *args, **kwargs):
#         #       video_file = request.FILES["video"]
#         # generate pre-signed URL for uploading the file

#         # upload the file
#         # with open(video_file.temporary_file_path(), "rb") as src:
#         #     default_storage.save(video_file.name, src)
#         # create the Video object and save it to the database
#         serializer = self.get_serializer(
#             data=request.data,
#             # context={"video_file": video_file}
#         )
#         if serializer.is_valid():
#             serializer.save(user=self.request.user)
#             headers = self.get_success_headers(serializer.data)
#             return Response(
#                 serializer.data, status=status.HTTP_201_CREATED, headers=headers
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = VideoSerializer(queryset, many=True)
#         return Response(serializer.data)

# https://www.hacksoft.io/blog/direct-to-s3-file-upload-with-django
class FileDirectUploadStartApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        file_name = serializers.CharField()
        file_type = serializers.CharField()

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = FileDirectUploadService(request.user)
        presigned_data = service.start(**serializer.validated_data)

        return Response(data=presigned_data)


class FileDirectUploadFinishApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        file_id = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_id = serializer.validated_data["file_id"]

        file = get_object_or_404(File, id=file_id)

        service = FileDirectUploadService(request.user)
        service.finish(file=file)

        return Response({"id": file.id})


class FileDirectUploadLocalApi(ApiAuthMixin, APIView):
    def post(self, request, file_id):
        file = get_object_or_404(File, id=file_id)

        file_obj = request.FILES["file"]

        service = FileDirectUploadService(request.user)
        file = service.upload_local(file=file, file_obj=file_obj)

        return Response({"id": file.id})
