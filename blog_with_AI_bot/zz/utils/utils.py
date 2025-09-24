# zz/utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.template.loader import render_to_string
from django.db import transaction

def notify_new_comment(comment):
    """
    Отправляет новый комментарий во все WebSocket-сессии группы 'comments'
    """
    channel_layer = get_channel_layer()
    group_name = f"post_{comment.post_id}"  # теперь группа по id поста
    print(f"📡 notify_new_comment → {group_name} id={comment.id}")
    
    def _send():
        html = render_to_string("comments/_comment.html", {"comment": comment})
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "comment_message",
                "comment": {
                    "id": comment.id,
                    "author": comment.author.username,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                    "parent_id": comment.parent_id if comment.parent_id else None,
                    "html": html,
                },
            },
        )
    transaction.on_commit(_send)
