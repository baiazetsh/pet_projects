#zz/management/commands/shitgen.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from zz.models import Topic, Chapter, Post, Comment
from zz.utils.ollama_client import check_model_availability
from zz.utils.ollama_prompts import  generate_with_template
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Нейроублюдок генерит Topic -> Chapter -> Post -> Comment (с сарказмом)"

    def add_arguments(self, parser):
        parser.add_argument("theme",
                            type=str, help="Основная тема для генерации")
        parser.add_argument("--chapters",
                            type=int, default=1,
                            help="Количество глав (по умолчанию: 1)")
        parser.add_argument("--posts",
                            type=int, default=1,
                            help="Постов на главу (по умолчанию: 1)")
        parser.add_argument("--comments",
                            type=int, default=1,
                            help="Комментариев на пост (по умолчанию: 1)")
        parser.add_argument("--retries",
                            type=int, default=3,
                            help="Попыток при ошибке (по умолчанию: 3)")
        parser.add_argument("--delay",
                            type=int, default=2,
                            help="Задержка между запросами (сек, по умолчанию: 2)")


    def handle(self, *args, **options):
        theme = options["theme"]
        chapters_count = options["chapters"]
        posts_per_chapter = options["posts"]
        comments_per_post = options["comments"]
        retries = options["retries"]
        delay = options["delay"]
        
        self.stdout.write(self.style.SUCCESS(
            f"""
            🚀 Generation context by theme: '{theme}'\n"
                Chapters: {chapters_count},
                Posts by chapter: {posts_per_chapter}
                Comments by post: {comments_per_post}"
            """
            ))
        
        # checking ollama model
        is_available, available_models = check_model_availability()
        if not is_available:
            self.stdout.write(self.style.ERROR(f"❌ Модель недоступна. Доступные модели: {available_models}"))
            return
              
        # Получаем или создаём бота        
        User = get_user_model()
        bot_user, created = User.objects.get_or_create(
            username="NeuroUbludok",
            defaults={
                'email': 'neuro@site.com',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f"  👤 Создан пользователь-бот: {bot_user.username}")

        try:
            # 1. Topic
            self.stdout.write("  📁 Creating Topic...")
            topic = Topic.objects.create(owner=bot_user, name=theme)
            self.stdout.write(f"  ✅ Topic created: {topic.name}")
            time.sleep(delay)
            
            total_posts = 0
            total_comments = 0            

            # 2. Chapter
            for chapter_num in range(1, chapters_count + 1):
                chapter_title = generate_with_template(
                    "chapter_title",
                    theme=theme,
                    num=chapter_num
                )                
                chapter = Chapter.objects.create(
                    topic=topic,
                    title=chapter_title,
                    description=f"Autogeneration. Chapter {chapter_num}"
                )
                self.stdout.write(f"\n  📗 Chapter {chapter_num}: {chapter.title}")
                time.sleep(delay)          

                # 3. Post
                for post_num in range(1, posts_per_chapter + 1):                    
                    self.stdout.write(f"    📝 Пост {post_num}/{posts_per_chapter}")
                    
                    # Генерируем заголовок поста
                    post_title = generate_with_template(
                    "post_title",
                    theme=theme,
                    num=post_num
                    )
                    post_content = generate_with_template(
                        "post_content",
                        theme=theme,
                        num=post_num
                    )
                    post = Post.objects.create(
                        chapter=chapter,
                        title=post_title,
                        content=post_content
                    )
                    total_posts += 1
                    self.stdout.write(f"  ✅  {post.title[:50]}...")
                    time.sleep(delay)

                    # 4. Comment
                    for comment_num in range(1, comments_per_post + 1):
                        self.stdout.write(f"    💬 comment{comment_num}/{comments_per_post}")

                        comment_text = generate_with_template(
                            "comment",
                            post_excerpt=post_content[:500],
                            num=comment_num
                        )                            
                        Comment.objects.create(
                            post=post,
                            author=bot_user,
                            content=comment_text
                        )
                        total_comments += 1
                        self.stdout.write(f"  ✅ Comment created: {comment_text[:60]}...")
                        time.sleep(delay * 0.5)
           
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