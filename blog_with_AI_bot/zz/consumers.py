# zz/consumers.py
import json
import logging
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from zz.serializers import CommentSerializer
from zz.utils.ollama_prompts import BOT_SYSTEM_PROMPTS
from zz.utils.ollama_client import generate_text, clean_response
from zz.models import ChatMessage
from zz.models import Comment

logger = logging.getLogger(__name__)


class CommentConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time comments on posts"""
    
    async def connect(self):
        self.post_id = self.scope["url_route"]["kwargs"]["post_id"]
        self.room_group_name = f"post_{self.post_id}"
        
        # Subscribe to group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"✅ WS connected to post={self.post_id}, channel={self.channel_name}")
        
        
    async def disconnect(self, close_code):
        # Unsubscribe from group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"⚠️ WS disconnected from post={self.post_id}, channel={self.channel_name}")
        
        
    async def receive(self, text_data):
        """Receive message from client and broadcast"""
        try:
            data = json.loads(text_data)
            comment_text = data.get("comment", "").strip()
            user = self.scope["user"]
            
            if not comment_text or not user.is_authenticated:
                return

            # create the comment in the DB
            comment = await self._create_comment(user, self.post_id, comment_text)

            # serial with avatar & quote
            serialized = await self._serialize_comment(comment)
            
            # Send to group chat
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "comment_message",
                    "comment": serialized,
                }
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Error in receive: {e}")
        
        
    #async def comment_message(self, event):
     #   """Handler for group messages"""
      #  await self.send(text_data=json.dumps(event["comment"]))
    async def comment_message(self, event):
        """Handler for group messages"""
        # 🔥 Отправляем весь словарь с HTML и ID родителя клиенту
        await self.send(text_data=json.dumps({
            "comment_html": event.get("comment_html"),
            "parent_id": event.get("parent_id"),
            "comment_id": event.get("comment_id"),
        }))


    # async wrapping
    @database_sync_to_async
    def _create_comment(self, user, post_id, content):
        return Comment.objects.create(author=user, post_id=post_id, content=content)


    @database_sync_to_async
    def _serialize_comment(self, comment):
        return CommentSerializer(comment).data




class ShitgenConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for content generation progress"""
    
    async def connect(self):
        self.group_name = "shitgen"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"✅ WS connected to shitgen, channel={self.channel_name}")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"⚠️ WS disconnected from shitgen, channel={self.channel_name}")


    async def progress_message(self, event):
        """Handler for progress messages"""
        await self.send(text_data=json.dumps({
            "message": event.get("message", "")
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for AI chat bots"""
    
    async def connect(self):
        self.group_name = "chat"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"✅ WS connected to chat, channel={self.channel_name}")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"⚠️ WS disconnected from chat, channel={self.channel_name}")


    async def receive(self, text_data=None, bytes_data=None):
        """Receive and process user message, generate bot response"""
        
        try:
            logger.info(f"📩 WS received message: {text_data}")

            data = json.loads(text_data)
            user_message = data.get("message", "").strip()
            bot_key = data.get("bot", "NeuroUbludok")
            
            if not user_message:
                await self.send(text_data=json.dumps({
                    "error": "Message cannot be empty"
                }))
                return
            
            user = self.scope["user"] if self.scope["user"].is_authenticated else None

            # Save user message to DB
            await self.save_message(user, bot_key, "user", user_message)
            
            # Generate bot response
            system_prompt = BOT_SYSTEM_PROMPTS.get(bot_key, "You are a helpful assistant")
            prompt = f"{system_prompt}\n\nUser: {user_message}\nBot:"
            
            try:
                raw_response = generate_text(prompt)
                reply = clean_response(raw_response)
            except Exception as e:
                reply = "Sorry, I couldn't generate a response right now."
                logger.error(f"Ollama generation error: {e}")

            # Save bot response to DB
            await self.save_message(user, bot_key, "bot", reply)

            # Send reply to client
            await self.send(text_data=json.dumps({
                "reply": reply,
                "bot": bot_key
            }))
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON format"
            }))
        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                "error": "Internal server error"
            }))


    @database_sync_to_async
    def save_message(self, user, bot_name, role, content):
        """Save message to database in separate thread"""
        return ChatMessage.objects.create(
            user=user,
            bot_name=bot_name,
            role=role,
            content=content
        )