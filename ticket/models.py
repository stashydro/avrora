from tkinter.constants import CASCADE

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    statuses = {
        'created': 'Создан',
        'processing': 'В работе',
        'completed': 'Завершен'
    }
    status = models.CharField(choices=statuses, default='created',max_length=20)