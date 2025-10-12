#zz/management/commands/shitgen.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from zz.models import Topic, Chapter, Post, Comment, Prompt, GeneratedItem
from zz.utils.ollama_client import(
    check_model_availability,
    generate_text,
    clean_response,
)
from zz.utils.ollama_prompts import  generate_with_template, BOT_SYSTEM_PROMPTS
import time
import logging
from zz.utils.llm_selector import generate_via_selector
from zz.utils.source_selector import get_active_source
from zz.utils.bots import BOTS


logger = logging.getLogger(__name__)

source = get_active_source() # func choice LLM model

class Command(BaseCommand):
    help = "Нейроублюдок генерит Topic -> Chapter -> Post -> Comment "

    def add_arguments(self, parser):
        parser.add_argument(
            "topic_theme",
            type=str,
            help="Основная тема для topic"
            )
        parser.add_argument(
            "--chapters",
            type=int,
            default=1,
            help="Количество глав (по умолчанию: 1)"
            )
        parser.add_argument(
            "--posts",
            type=int,
            default=1,
            help="Постов на главу (по умолчанию: 1)"
            )
        parser.add_argument(
            "--comments",
            type=int,
            default=1,
            help="Комментариев на пост (по умолчанию: 1)"
            )
        parser.add_argument(
            "--bot",
            type=str,
            default="NeuroUbludok",
            choices=[b["username"] for b in BOTS],
            help="Character of bot"
        )
        parser.add_argument(
            "--source",
            type=str,
            default="ollama",
            choices=["ollama", "grok", "local"],
            help="Te source of model generation (default: ollama)"
        )
        parser.add_argument(
            "--retries",
            type=int,
            default=3,
            help="Попыток при ошибке (по умолчанию: 3)"
            )
        parser.add_argument(
            "--delay",
            type=int,
            default=1,
            help="Задержка между запросами (сек, по умолчанию: 1)"
            )


    def handle(self, *args, **options):
        topic_theme = options["topic_theme"]
        chapters_count = options["chapters"]
        posts_per_chapter = options["posts"]
        bot_personality = options["bot"]
        comments_per_post = options["comments"]
        retries = options["retries"]
        delay = options["delay"]
        source = options["source"].lower()
        
        self.stdout.write(self.style.SUCCESS(
            f"""
            🚀 Generation context by theme: '{topic_theme}'\n"
                Chapters: {chapters_count},
                Posts by chapter: {posts_per_chapter}
                Comments by post: {comments_per_post}
                Bot: {bot_personality}
            """
            ))
        
        # checking ollama model
        is_available, available_models = check_model_availability()
        if not is_available:
            self.stdout.write(self.style.ERROR(f"❌ Модель недоступна. Доступные модели: {available_models}"))
            return
              
        # Получаем или создаём бота        
        User = get_user_model()
        try:
            bot_user = User.objects.get(username=bot_personality)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"!!! Bot {bot_personality} not found. Create the bot, before thru initbots.py"
            ))
            return            
            
        #if _:
        #    self.stdout.write(f"  👤 Создан пользователь-бот: {bot_user.username}")

        try:
            # 1. Topic
            self.stdout.write("  📁 Creating Topic...")
            topic = Topic.objects.create(
                owner=bot_user,
                name=topic_theme,
                
                )
            self.stdout.write(f"  ✅ Topic created: {topic.name}")
            time.sleep(delay)
            
            total_posts = 0
            total_comments = 0   
                   

            # 2. Chapter
            for chapter_num in range(1, chapters_count + 1):
                chapter_title = generate_with_template(
                    "chapter_title",
                    theme=topic_theme,
                    num=chapter_num,
                    #source=source
                )                
                
                chapter_description = generate_with_template(
                    "chapter_description",
                    theme=topic_theme,
                    num=chapter_num,
                    #source=source
                )
                
                chapter = Chapter.objects.create(
                    topic=topic,
                    title=chapter_title,
                    description=chapter_description,
                    author=topic.owner
                )
                self.stdout.write(f"\n  📗 Chapter {chapter_num}: {chapter.title}")
                time.sleep(delay)

                # 🔥 Отправляем прогресс в WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "shitgen",
                    {
                        "type": "progress_message",
                        "message": f"📗 Chapter {chapter_num} created: {chapter.title}"
                    }
                )       

                # 3. Post
                for post_num in range(1, posts_per_chapter + 1):                    
                    self.stdout.write(f"    📝 Пост {post_num}/{posts_per_chapter}")
                    
                    # Генерируем заголовок поста
                    post_title = generate_with_template(
                    "post_title",
                    theme=chapter_title,
                    num=post_num,
                    #source=source
                    )
                    post_content = generate_with_template(
                        "post_content",
                        theme=chapter_title,
                        num=post_num,
                        #source=source
                    )
                    post = Post.objects.create(
                        chapter=chapter,
                        title=post_title,
                        content=post_content,
                        author=bot_user,
                    )
                    total_posts += 1
                    self.stdout.write(f"  ✅  {post.title[:50]}...")
                    time.sleep(delay)


                    # 🔥 Отправляем прогресс в WebSocket
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        "shitgen",
                        {
                            "type": "progress_message",
                            "message": f"📗 Chapter {chapter_num} created: {chapter.title}"
                        }
                    )

                    # 4. Comment
                    for comment_num in range(1, comments_per_post + 1):
                        self.stdout.write(f"    💬 comment{comment_num}/{comments_per_post}")

                        comment_text = generate_with_template(
                            "comment",
                            post_excerpt=post_content[:500],
                            num=comment_num,
                            #Ssource=source
                        )                            
                        Comment.objects.create(
                            post=post,
                            author=bot_user,
                            content=comment_text,
                            bot_replied=True
                        )
                        total_comments += 1
                        self.stdout.write(f"  ✅ Comment created: {comment_text[:60]}...")
                        time.sleep(delay * 0.5)

                        # 🔥 WS прогресс
                        async_to_sync(channel_layer.group_send)(
                            "shitgen",
                            {
                                "type": "progress_message",
                                "message": f"💬 Comment {comment_num} added to {post.title[:30]}"
                            }
                        )
           
            # Final report
            self.stdout.write(self.style.SUCCESS(
                f"\n🎉 Generation completed!\n"
                f"   Topic: {topic.name}\n"
                f"   Chapters: {chapters_count}\n"
                f"   Posts: {total_posts}\n"
                f"   Comments: {total_comments}\n"
                f"   Author: {bot_user.username}\n"
            ))

        except Exception as e:
            logger.error(f"Critical error: {e}")
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
            raise           