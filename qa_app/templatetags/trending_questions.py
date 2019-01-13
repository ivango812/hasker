from django import template
from ..models import Question
from django.conf import settings

register = template.Library()


@register.inclusion_tag('_trending_questions.html')
def get_trending_questions():
    return {'trending_questions': Question.get_trending()[:settings.TRENDING_QUESTIONS]}
