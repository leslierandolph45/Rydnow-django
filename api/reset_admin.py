from django.http import HttpResponse
from django.contrib.auth.models import User


def reset_admin(request):
    try:
        user = User.objects.get(username='admin')
        user.set_password('Admin123!')
        user.save()
        return HttpResponse('✅ PASSWORD UPDATED! Username: admin  Password: Admin123!')
    except User.DoesNotExist:
        User.objects.create_superuser('admin', 'admin@example.com', 'Admin123!')
        return HttpResponse('✅ NEW ADMIN CREATED! Username: admin  Password: Admin123!')
