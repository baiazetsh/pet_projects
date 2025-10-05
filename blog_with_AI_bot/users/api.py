# users/api.py

from rest_framework import serializers, generics
from .models import Profile
from zz.models import Post


class PostShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "created_at", "get_absolute_url", "content"]

class ProfileSerializer(serializers.ModelSerializer):
    #display_name = serializers.CharField(source="display_name", read_only=True)
    display_name = serializers.CharField(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    last_posts = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["id", "display_name", "avatar_url", "bio", "quote", "is_bot", "last_posts"]

    def get_avatar_url(self, obj):
        # возвращаем абсолютный URL, если request доступен
        request = self.context.get("request")
        url = obj.avatar_url
        if request and url and url.startswith("/"):
            return request.build_absolute_uri(url)
        return url
    
    def get_last_posts(self, obj):
        posts = obj.user.posts.order_by("-created_at")[:3]
        #posts = Post.objects.filter(author=obj.user).order_by("-created_at")[:3]
        return PostShortSerializer(posts, many=True, context=self.context).data

class ProfileDetailAPI(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
