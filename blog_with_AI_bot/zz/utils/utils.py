# zz/utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.template.loader import render_to_string
from django.db import transaction
from zz.serializers import CommentSerializer

def notify_new_comment(comment):
    """
    Отправляет новый комментарий во все WebSocket-сессии группы 'comments'
    """
    channel_layer = get_channel_layer()
    group_name = f"post_{comment.post_id}"  

    print(f"📡 notify_new_comment → {group_name} id={comment.id}")
    
    def _send():
        print(f"📡 Rendering and sending notification for comment {comment.id} to group {group_name}")

        # 1. Render the comment to an HTML string using the existing template
        html = render_to_string("zz/_comment.html", {"comment": comment})

        # 2. Determine if the comment is a reply to get the parent ID
        parent_id = comment.parent.id if comment.parent else None

        # 3. Construct the payload with the rendered HTML and necessary IDs
        payload = {
            "type": "comment_message",  # Matches the handler name in consumer.py
            "comment_html": html,
            "parent_id": parent_id,
            "comment_id": comment.id,
        }
        
        # 4. Send the payload to the WebSocket group
        async_to_sync(channel_layer.group_send)(group_name, payload)
        print(f"✅ Successfully sent message for comment {comment.id} to {group_name}")
        
    transaction.on_commit(_send)
