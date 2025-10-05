from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from zz.models import Post
from zz.signals import call_ubludok

def summon_ubludok(request, pk):
    """AJAX-обработчик кнопки 'Позвать ублюдка'"""
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        post = get_object_or_404(Post, pk=pk)

        # 🔥 запускаем сигнал, который дальше дергает Celery
        call_ubludok.send(sender=None, user=request.user, post=post)

        # 🔥 возвращаем чистый JSON, не HTML
        response = JsonResponse({
            "success": True,
            "message": f"The bastard is called for post {post.id}"
        })
        response["Content-Type"] = "application/json"   # подстраховка для браузеров
        return response

    # если не POST или не AJAX
    return JsonResponse(
        {"success": False, "message": "Invalid request"},
        status=400
    )
