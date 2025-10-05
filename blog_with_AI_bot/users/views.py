#users/views.py

#from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.contrib.auth import get_user_model
from users.models import Profile
from zz.models import Post


"""
class ProfileListView(ListView):
    model = Profile
    template_name = "users/profile_list.html"
    context_object_name = "profiles"
"""

class ProfileDetailView(DetailView):
    model = Profile
    template_name = "users/profile_detail.html"
    context_object_name = "profile"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # all user posts 
        context["posts"] = Post.objects.filter(author=self.object.user).order_by("-created_at")
        return context