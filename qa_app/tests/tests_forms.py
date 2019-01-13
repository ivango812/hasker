from django.test import TestCase, Client
from ..models import Tag
from ..forms import QuestionForm


class QuestionFromTestCase(TestCase):

    def setUp(self):
        Tag.objects.create(pk=1, name='Тег1')
        Tag.objects.create(pk=2, name='Тег2')
        Tag.objects.create(pk=3, name='Тег3')
        Tag.objects.create(pk=4, name='Тег4')
        Tag.objects.create(pk=5, name='Тег5')

    def test_question_form(self):
        form_data = {'title':'Тайтл вопроса', 'content': 'Содержание вопроса', 'tags': []}
        question_form = QuestionForm(data=form_data)
        self.assertTrue(question_form.is_valid())
        form_data = {'title':'Тайтл вопроса', 'content': 'Содержание вопроса', 'tags': [1]}
        question_form = QuestionForm(data=form_data)
        self.assertTrue(question_form.is_valid())
        form_data = {'title':'Тайтл вопроса', 'content': 'Содержание вопроса', 'tags': [1, 2, 3]}
        question_form = QuestionForm(data=form_data)
        self.assertTrue(question_form.is_valid())
        form_data = {'title':'Тайтл вопроса', 'content': 'Содержание вопроса', 'tags': [1, 2, 3, 4]}
        question_form = QuestionForm(data=form_data)
        self.assertFalse(question_form.is_valid())
