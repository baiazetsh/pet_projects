#zz/management/commands/shitgen.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from zz.models import Topic, Chapter, Post, Comment
from zz.utils.ollama_client import generate_text, list_models
import re
import time
import random
import logging
from django.conf import settings
#import django.dispatch
from django.dispatch import receiver, Signal

# Настройка логгера
logger = logging.getLogger(__name__)

call_ubludok = Signal()

#@receiver(call_ubludok)
#def handle_call_ubludok(sender, **kwargs):
#    print("⚡ Нейроублюдок призван!")


def clean_response(text):
    """Удаляет служебные теги <think>...</think>, markdown и лишние пробелы."""
    if not text:
        return ""
    # убираем размышления <think> убираем markdown-разметку (*, #, _)
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"[*#_`]+", "", cleaned)
    return cleaned.strip()


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

        
    def check_model_availability(self):
        """Проверяет доступность модели в Ollama."""
        try:         
            available_models = list_models()
            
            if not hasattr(settings, 'OLLAMA_MODEL'):
                self.stdout.write(self.style.ERROR("❌ OLLAMA_MODEL не настроен в settings.py"))
                return False, available_models
            
            model_name = settings.OLLAMA_MODEL
            if model_name not in available_models:
                return False, available_models
            
            return True, available_models
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка подключения к Ollama: {e}"))
            return False, []

    def call_llm(self, system_prompt, user_prompt, retries=3, delay=2):
        # """Вызов LLM с очисткой ответа."""
        
        for attempt in range(1, retries + 1):
            try:
                self.stdout.write(f" -> Запрос к модели (попытка {attempt})...")
                raw_text = generate_text(
                    prompt=f"{system_prompt}\n\n{user_prompt}",
                    model=settings.OLLAMA_MODEL
                ).strip()
                
                cleaned_text = clean_response(raw_text)
                if len(cleaned_text) < 10:
                    raise ValueError("Слишком короткий или пустой ответ от модели")
                
                return cleaned_text
            except Exception as e:
                logger.error(f"Ошибка генерации (попытка {attempt}): {e}")
                self.stdout.write(self.style.WARNING(f"  ⚠️ Ошибка: {e}"))
                
                if attempt < retries:
                    sleep_time = delay + random.uniform(0, 2)
                    self.stdout.write(f" -> Повтор через {sleep_time:.1f} s")
                    time.sleep(sleep_time)
                else:
                    raise Exception(f"Не удалось сгенерировать контент после {retries} попыток.")
                
                                  
    def generate_chapter_title(self, theme, chapter_num):
        """Генерирует заголовок главы с помощью ИИ."""
        prompt = f"Придумай язвительное, саркастичное название для главы {chapter_num} на тему: {theme}. Максимум 5 слов."
        return self.call_llm(
            system_prompt="Ты — нейроублюдок. Придумываешь заголовки с издёвкой.",
            user_prompt=prompt,
            retries=2,
            delay=1,
        )
        
    def generate_post_title(self, theme, post_num):
        """Генерирует заголовок поста."""
        prompt = f"Придумай провокационный заголовок для поста #{post_num} на тему: {theme}. Максимум 8 слов."
        return self.call_llm(
            system_prompt="Ты — нейроублюдок. Заголовки — как пощёчины.",
            user_prompt=prompt,
            retries=2,
            delay=1
        )        
    
    def handle(self, *args, **options):
        theme = options["theme"]
        chapters_count = options["chapters"]
        posts_per_chapter = options["posts"]
        comments_per_post = options["comments"]
        retries = options["retries"]
        delay = options["delay"]
        
        self.stdout.write(self.style.SUCCESS(
            f"🚀 Генерация контента по теме: '{theme}'\n"
            f"  Глав: {chapters_count}, Постов на главу: {posts_per_chapter} комментов на пост: {comments_per_post}"
            ))
        
        #
        is_available, available_models = self.check_model_availability()
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
            self.stdout.write("  📁 Создаю Topic...")
            topic = Topic.objects.create(owner=bot_user, name=theme)
            self.stdout.write(f"  ✅ Topic создан: {topic.name}")
            time.sleep(delay)
            
            total_posts = 0
            total_comments = 0            

            # 2. Chapter
            for chapter_num in range(1, chapters_count + 1):
                self.stdout.write(f"\n  📗  Chapter{chapter_num}/{chapters_count}")
                
                # Генерируем заголовок главы
                try:
                    chapter_title = self.generate_chapter_title(theme, chapter_num)
                except Exception:
                    chapter_title = f"Глава {chapter_num}: Что-то пошло не так, но мы продолжаем"
                    
                chapter = Chapter.objects.create(
                    topic=topic,
                    title=chapter_title,
                    description=f"Автогенерация. Глава {chapter_num}. Нейроублюдок в ударе."
                )
                self.stdout.write(f"  ✅ Chapter создан: {chapter.title}")
                time.sleep(delay)

                # 3. Post
                for post_num in range(1, posts_per_chapter + 1):                    
                    self.stdout.write(f"    📝 Пост {post_num}/{posts_per_chapter}")
                    
                    # Генерируем заголовок поста
                    try:
                        post_title = self.generate_post_title(theme, post_num)
                    except Exception:
                        post_title = f"Пост№ {post_num}  без заголовка, зато с матом"
                     
                    # Генерируем содержание поста   
                    post_prompt =(
                        f"Напиши пост длиной 1000–1500 символов по теме: {theme}."
                        f"Будь максимально язвительным, саркастичным, провокационным. Без разметки. "
                        f"Это {post_num}-й пост в серии."
                    )
                    try:
                        post_content = self.call_llm(
                            system_prompt="Ты — нейроублюдок. Пишешь посты с едким сарказмом, как кислота на нервы.",
                            user_prompt=post_prompt,
                            retries=retries,
                            delay=delay
                        )
                    except Exception:
                        post_content = "Пост не сгенерировался. Виноваты все, кроме меня."

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
                        self.stdout.write(f"    💬 коммент{comment_num}/{comments_per_post}")
                        
                        comment_prompt = (
                            f"Оставь язвительный, саркастичный комментарий к этому посту:\n\n"
                            f"{post_content[:500]}\n\n"
                            f"Не повторяй пост. Будь оригинален. Это {comment_num}-й комментарий."
                        )
                        try:
                            
                            comment_content = self.call_llm(
                                system_prompt="Ты — нейроублюдок. Твои комменты — как нож в спину, но с улыбкой.",
                                user_prompt=comment_prompt,
                                retries=retries,
                                delay=delay
                            )
                        except Exception:
                            comment_content = "Коммент не удался. Представьте, что тут что-то очень обидное."
                            

                        Comment.objects.create(
                            post=post,
                            author=bot_user,
                            content=comment_content
                        )
                        total_comments += 1
                        self.stdout.write(f"  ✅ Комментарий создан: {comment_content[:60]}...")
                        time.sleep(delay * 0.5)
                    
            # Финальный отчёт
            self.stdout.write(self.style.SUCCESS(
                f"\n🎉 Генерация завершена!\n"
                f"   Topic: {topic.name}\n"
                f"   Глав: {chapters_count}\n"
                f"   Постов: {total_posts}\n"
                f"   Комментариев: {total_comments}\n"
                f"   Автор: {bot_user.username}\n"
            ))

        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            self.stdout.write(self.style.ERROR(f"❌ Ошибка: {e}"))
            raise