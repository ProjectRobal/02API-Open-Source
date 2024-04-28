from django.contrib import admin
from .models import Topic,TopicForm,TopicCatcher,TopicBeamer

# Register your models here.

class AdminTopic(admin.ModelAdmin):
    form=TopicForm

admin.site.register(Topic,AdminTopic)
admin.site.register(TopicCatcher,AdminTopic)
admin.site.register(TopicBeamer,AdminTopic)
