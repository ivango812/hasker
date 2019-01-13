from django.test import TestCase, Client
from django.urls import reverse
from ..models import Question, Answer, User, Tag, Vote
import tempfile


class IndexViewTestCase(TestCase):

    def _create_image(self):
        from PIL import Image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image = Image.new('RGB', (200, 200), 'white')
            image.save(f, 'PNG')
        return open(f.name, mode='rb')

    def setUp(self):
        self.user = User.objects.create_user(username='username1', password='f0sP94Mfk1Cs')
        self.user2 = User.objects.create_user(username='username2', password='f0sP94Mfk1Cs')
        self.image = self._create_image()

    def tearDown(self):
        self.image.close()

    def test_index_view(self):
        for i in range(1, 10):
            Question.objects.create(author=self.user, title='Заголовок вопроса{}'.format(i), content='Текст вопроса')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertFalse(response.context['is_paginated'])
        self.assertEqual(len(response.context['last_questions']), 9)

        for i in range(10, 18):
            Question.objects.create(author=self.user, title='Заголовок вопроса{}'.format(i), content='Текст вопроса')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['last_questions']), 10)
        response = self.client.get(reverse('index')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['last_questions']), 7)

    def test_index_hot_view(self):
        for i in range(1, 10):
            Question.objects.create(author=self.user, title='Заголовок вопроса{}'.format(i), content='Текст вопроса')
        response = self.client.get(reverse('hot'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertFalse(response.context['is_paginated'])
        self.assertEqual(len(response.context['last_questions']), 9)

        for i in range(10, 18):
            Question.objects.create(author=self.user, title='Заголовок вопроса{}'.format(i), content='Текст вопроса')
        response = self.client.get(reverse('hot'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['last_questions']), 10)
        response = self.client.get(reverse('hot')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['last_questions']), 7)

    def test_question_create_view(self):
        self.client.login(username='username1', password='f0sP94Mfk1Cs')
        response = self.client.post(reverse('new_question'), data={'title': 'Заголовок', 'content': 'Содержание'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/question/', response.url)

        self.client.logout()
        response = self.client.post(reverse('new_question'), data={'title': 'Заголовок', 'content': 'Содержание'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login')+'?next='+reverse('new_question'))

    def test_answer_create_view(self):
        self.client.login(username='username1', password='f0sP94Mfk1Cs')
        response_question_new = self.client.post(reverse('new_question'), data={'title': 'Заголовок', 'content': 'Содержание'})
        response = self.client.post(response_question_new.url, data={'content': 'Ответ'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'You need to <a href="/login">Login</a> first.')
        self.client.logout()

        response = self.client.post(response_question_new.url, data={'content': 'Ответ'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You need to <a href="/login">Login</a> first.')

    def test_search_text_view(self):
        for i in range(1, 10):
            Tag.objects.create(pk=i, name='Тег{}'.format(i))
        for i in range(1, 30):
            title = 'Вопрос{}'.format(i)
            context = 'Тело{}'.format(i)
            tag = i % 5 + 1
            if i < 10:
                title += ' слово1'
                context += ' слово2'
            elif i < 20:
                title += ' слово3'
                context += ' слово4'
            question = Question.objects.create(author=self.user, title=title, content=context)
            question.tags.add(tag)

        response = self.client.get(reverse('search')+'?q=слово2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['found_questions']), 9)

        response = self.client.get(reverse('search')+'?q=слово3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['found_questions']), 10)

        response = self.client.get(reverse('search')+'?q=слово')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['found_questions']), 19)

    def test_search_text_paginator_view(self):
        for i in range(1, 30):
            Question.objects.create(author=self.user, title='Вопрос{}'.format(i), content='Тело{}'.format(i))

        response = self.client.get(reverse('search')+'?q=вопрос')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['found_questions']), 20)

        response = self.client.get(reverse('search')+'?q=вопрос&page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['found_questions']), 9)

    def test_search_tag_view(self):
        for i in range(1, 10):
            Tag.objects.create(pk=i, name='Тег{}'.format(i))
        for i in range(1, 30):
            title = 'Вопрос{}'.format(i)
            context = 'Тело{}'.format(i)
            tag = i % 5 + 1
            if i < 10:
                title += ' слово1'
                context += ' слово2'
            elif i < 20:
                title += ' слово3'
                context += ' слово4'
            question = Question.objects.create(author=self.user, title=title, content=context)
            question.tags.add(tag)

        response = self.client.get(reverse('search')+'?q=tag:слово2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['found_questions']), 0)

        response = self.client.get(reverse('search')+'?q=tag:Тег1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['found_questions']), 5)
        response = self.client.get(reverse('search')+'?q=tag:  Тег2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['found_questions']), 6)

    def test_right_answer_view(self):
        question = Question.objects.create(author=self.user, title='Вопрос1', content='Содержание')
        answer1 = question.answers.create(author=self.user2, content='Ответ1')
        answer2 = question.answers.create(author=self.user, content='Ответ2')
        answer3 = question.answers.create(author=self.user2, content='Ответ3')

        response = self.client.get(reverse('right_answer', kwargs={'pk': answer1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login')+'?next='+reverse('right_answer', kwargs={'pk': answer1.pk}))

        self.client.force_login(self.user2)
        response = self.client.get(reverse('right_answer', kwargs={'pk': answer1.pk}))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('right_answer', kwargs={'pk': 39482347}))
        self.assertEqual(response.status_code, 405)

        self.client.force_login(self.user)
        response = self.client.get(reverse('right_answer', kwargs={'pk': answer1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('question', kwargs={'pk': question.pk}))

        self.client.force_login(self.user)
        response = self.client.get(reverse('right_answer', kwargs={'pk': answer3.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('question', kwargs={'pk': question.pk}))

    def test_vote_view(self):
        question = Question.objects.create(author=self.user, title='Вопрос1', content='Содержание')
        answer1 = question.answers.create(author=self.user2, content='Ответ1')
        answer2 = question.answers.create(author=self.user, content='Ответ2')
        answer3 = question.answers.create(author=self.user2, content='Ответ3')
        question_url = reverse('question', kwargs={'pk': question.pk})

        requested_url = reverse('vote', kwargs={'model_entity': 'question', 'pk': question.pk, 'value_alias': 'like'})
        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login')+'?next='+requested_url)

        requested_url = reverse('vote', kwargs={'model_entity': 'answer', 'pk': answer1.pk, 'value_alias': 'like'})
        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login')+'?next='+requested_url)

        self.client.force_login(self.user)
        requested_url = reverse('vote', kwargs={'model_entity': 'question', 'pk': question.pk, 'value_alias': 'like'})
        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, question_url)
        self.assertEqual(question.votes_sum, 1)

        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, question_url)
        self.assertEqual(question.votes_sum, 1)

        requested_url = reverse('vote', kwargs={'model_entity': 'answer', 'pk': answer1.pk, 'value_alias': 'like'})
        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, question_url)
        self.assertEqual(answer1.votes_sum, 1)

        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, question_url)
        self.assertEqual(answer1.votes_sum, 1)

        requested_url = reverse('vote', kwargs={'model_entity': 'question', 'pk': question.pk, 'value_alias': 'dislike'})
        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, question_url)
        self.assertEqual(question.votes_sum, -1)

        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, question_url)
        self.assertEqual(question.votes_sum, -1)

        requested_url = reverse('vote', kwargs={'model_entity': 'answer', 'pk': answer1.pk, 'value_alias': 'dislike'})
        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, question_url)
        self.assertEqual(answer1.votes_sum, -1)

        response = self.client.get(requested_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, question_url)
        self.assertEqual(question.votes_sum, -1)

    def test_user_profile_edit_view(self):
        profile_url = reverse('profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login')+'?next='+profile_url)

        self.client.force_login(self.user)
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(profile_url, data={'username': self.user.username,
                                                       'email': 'test@yandex.ru',
                                                       'avatar': self.image})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account'))
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.email, 'test@yandex.ru')
