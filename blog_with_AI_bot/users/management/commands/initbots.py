# users/management/commands/initbots.py
# кастомной команды initbots, которая будет
# создавать ботов, только если их ещё нет (без ошибок дубляжа)
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile

User = get_user_model()


BOT_DATA = [
    {
        "username": "NeuroBatya",
        "email": "batya@example.com",
        "bio": "Добродушный старый робот в очках и майке.",
        "quote": "Ну, ребята, я вас научу жизни!",
        "avatar": "avatars/neurobatya.png",
    },
    {
        "username": "NeuroPsina",
        "email": "psina@example.com",
        "bio": "Злобная, саркастичная робособака на пенсии.",
        "quote": "Гав-гав, иди учись уму-разуму!",
        "avatar": "avatars/neuropsina.png",
    },
    {
        "username": "NeuroUbludok",
        "email": "ubludok@example.com",
        "bio": "Жесткий, бывалый бывший военный робот.",
        "quote": "Ну что, салаги, готовы к срачу?",
        "avatar": "avatars/neuroubludok.png",
    },
]


class Command(BaseCommand):
    help = "Инициализация бот-пользователей и их профилей"

    def handle(self, *args, **options):
        for bot in BOT_DATA:
            user, created = User.objects.get_or_create(
                username=bot["username"],
                defaults={
                    "email": bot["email"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан User: {user.username}"))
            else:
                self.stdout.write(self.style.WARNING(f"User {user.username} уже есть"))

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = bot["bio"]
            profile.quote = bot["quote"]
            profile.is_bot = True
             
            
            # we update the avatar only if it is still empty
            DEFAULT_AVATAR = "avatars/defaultava.png"
            
            if not profile.avatar or str(profile.avatar) == DEFAULT_AVATAR:
                profile.avatar = bot["avatar"] 
                
            profile.save()

            self.stdout.write(self.style.SUCCESS(f"Profile обновлён: {user.username}"))
