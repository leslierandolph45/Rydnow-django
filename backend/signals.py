from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import os


User = get_user_model()


@receiver(post_migrate)
def create_superuser_on_first_start(sender, **kwargs):
    username = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin45')
    email = os.environ.get('DJANGO_ADMIN_EMAIL', 'leslielrandolph45@gmail.com')
    password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'Admin@123')


    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print("✅ Superuser created")
    else:
        print("ℹ️ Superuser already exists")
