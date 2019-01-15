from django.db import models
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import truncatechars
from sorl import thumbnail
from django.db.models import Count, Q, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class User(AbstractUser):
    avatar = thumbnail.ImageField(verbose_name='Avatar', upload_to='avatars', blank=False)


class Tag(models.Model):
    name = models.CharField(verbose_name='Тег', max_length=64, blank=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    title = models.CharField(verbose_name='Заголовок вопроса', max_length=256, blank=False)
    content = models.TextField(verbose_name='Текст вопроса', max_length=16384, blank=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='questions', on_delete=models.CASCADE, blank=False)
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True)

    class Meta:
        ordering = ['-id']

    # TODO: change to cashed BooleanField
    @property
    def has_answer(self):
        return bool(self.answers.filter(is_right=True))

    @property
    def votes_sum(self):
        votes = self.votes.aggregate(Sum('value'))
        return votes['value__sum'] if votes['value__sum'] else 0

    def get_sorted_answers(self):
        return self.answers.annotate(sum_votes=Sum('votes__value')).order_by('-is_right', '-sum_votes', 'created_at')

    @staticmethod
    def get_last():
        return Question.objects.annotate(count_answers=Count('answers')).order_by('-created_at', '-id')

    @staticmethod
    def get_hot():
        return Question.objects.annotate(count_answers=Count('answers')).order_by('-count_answers', '-id')

    @staticmethod
    def get_trending():
        return Question.objects.annotate(count_votes=Count('votes')).order_by('-count_votes', '-id')

    @staticmethod
    def search(text):
        return Question.objects.filter(Q(title__icontains=text) | Q(content__icontains=text))\
            .annotate(count_answers=Count('answers')).order_by('-id')

    @staticmethod
    def get_by_tag(tag_name):
        try:
            return Tag.objects.get(name__iexact=tag_name).questions.all().order_by('-id')
        except Tag.DoesNotExist:
            return Question.objects.none()

    @staticmethod
    def get_by_user(user):
        return Question.objects.filter(author=user).annotate(count_answers=Count('answers')).order_by('-created_at')

    def __str__(self):
        return truncatechars(self.title, 64)


class Answer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    content = models.TextField(max_length=16384, blank=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False)
    is_right = models.BooleanField(verbose_name='Правильный ответ', default=False)

    @property
    def content_short(self):
        return truncatechars(self.content, 64)

    @property
    def votes_sum(self):
        votes = self.votes.aggregate(Sum('value'))
        return votes['value__sum'] if votes['value__sum'] else 0

    @staticmethod
    def get_by_user(user):
        return Answer.objects.filter(author=user).order_by('-created_at')

    def __str__(self):
        return self.content_short


class Vote(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    value = models.SmallIntegerField(verbose_name='Оценка')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True, related_name='votes')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True, related_name='votes')

    def __str__(self):
        return self.user.username + ' voted ' + str(self.value)

    @staticmethod
    def vote(model_object, user, value):
        object_name = 'question' if type(model_object) is Question else 'answer'
        try:
            vote = Vote.objects.get(**{object_name: model_object}, user=user)
            vote.value = value
            vote.save()
        except ObjectDoesNotExist:
            Vote.objects.create(**{object_name: model_object}, user=user, value=value)

    class Meta:
        unique_together = (('user', 'question'), ('user', 'answer'))
