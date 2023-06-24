from django.contrib import admin
from .models import Topic,TopicForm

# Register your models here.

class AdminTopic(admin.ModelAdmin):
    form=TopicForm

admin.site.register(Topic,AdminTopic)