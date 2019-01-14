from django.contrib import admin
from qa_app.models import Tag, Question, Answer, Vote, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import UserCreationForm
from sorl.thumbnail.admin import AdminImageMixin


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'created_at')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'content_short', 'is_right', 'author', 'created_at')


class UserAdmin(AdminImageMixin, BaseUserAdmin):
    add_form = UserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'avatar', 'password1', 'password2')}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.fieldsets[1][1]['fields'] += ('avatar',)
        super().__init__(*args, **kwargs)


# admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'value', 'question', 'answer')
