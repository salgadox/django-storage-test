from rest_framework import serializersfrom django_storage_test.videos.models import Videoclass VideoSerializer(serializers.ModelSerializer):    class Meta:        model = Video        fields = ("id", "user", "video")
