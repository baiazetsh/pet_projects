#zz/serializers.py

from rest_framework import serializers
from users.models import Profile
from zz.models import Comment


class ProfileMiniSerializer(serializers.ModelSerializer):
    """Short info about user for comments"""
    class Meta:
        models = Profile
        fields = ["avatar", "quote"]


class CommentSerializer(serializers.ModelSerializer):
    """Serializing comments with included author profile"""
    author_username = serializers.CharField(source="author.username", read_only=True)
    author_profile = ProfileMiniSerializer(source="author.profile", read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            "content",
            "author_username",
            "author_profile",
        ]
