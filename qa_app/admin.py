from django.contrib import admin
from qa_app.models import Tag, Question, Answer, Vote, User  #, UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import UserCreationForm
# from django.contrib.auth.models import User


# class AnswerTagInline(admin.TabularInline):
#     model = Answer.tags.though
#     extra = 0
#     extra = 1
    # raw_id_fields = ('answer', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    # inlines = [AnswerTagInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'created_at')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'content_short', 'is_right', 'author', 'created_at')
    # inlines = [AnswerTagInline]
    # pass


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     pass


# class ProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
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



# class MembershipInline(admin.TabularInline):
#     model = Group.members.through

#
# @admin.register(Person)
# class PersonAdmin(admin.ModelAdmin):
#     # inlines = [
#     #     MembershipInline,
#     # ]
#     pass
#
#
# @admin.register(Group)
# class GroupAdmin(admin.ModelAdmin):
#     # inlines = [
#     #     MembershipInline,
#     # ]
#     pass
#     # exclude = ('members',)
