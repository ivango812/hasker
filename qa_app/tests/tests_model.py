from django.test import TestCase, Client
from ..models import Question, Answer, User, Tag, Vote


class QuestionTestCase(TestCase):

    def setUp(self):
        # username = 'testuser1'
        # password = '7UhDZMBV5z'
        self.user1 = User.objects.create(pk=2, username='testuser1', password='7UhDZMBV5z')
        self.user2 = User.objects.create(pk=3, username='testuser2', password='7UhDZMBV5z')
        self.user3 = User.objects.create(pk=4, username='testuser3', password='7UhDZMBV5z')
        self.user4 = User.objects.create(pk=5, username='testuser4', password='7UhDZMBV5z')
        self.user5 = User.objects.create(pk=6, username='testuser5', password='7UhDZMBV5z')
        Tag.objects.create(name='название тега1')
        Tag.objects.create(name='название тега2')
        Tag.objects.create(name='название тега3')
        Tag.objects.create(name='название тега4')
        Tag.objects.create(name='название тега5')
        # self.question = Question.objects.create(title='Вопрос1?', content='Aaa?', author=self.user)
        # Answer(question=self.question, author=self.user, content='Ответ1')
        # Answer(question=self.question, author=self.user, content='Ответ2', is_right=True)
        # Answer(question=self.question, author=self.user, content='Ответ3')
        # self.question.answers.add(author=self.user, content='Ответ2')
        # self.question.answers.add(author=self.user, content='Ответ3')

    @classmethod
    def setUpTestData(cls):
        pass

    # def login(self):
    #     self.client.force_login(self.user1)
    #     # self.client.force_login(username=self.username, password=self.password)

    def test_question_create(self):
        question = Question.objects.create(author=self.user1,
                                           title='Сколько сейчас времени?',
                                           content='Содержание вопроса')
        self.assertTrue(question)
        self.assertTrue(question.created_at)
        self.assertEqual(question.author, self.user1)
        self.assertEqual(question.title, 'Сколько сейчас времени?')
        self.assertEqual(question.content, 'Содержание вопроса')

    def test_question_tag_create(self):
        question = Question.objects.create(author=self.user1, title='1', content='2')
        question.tags.set(Tag.objects.all()[:3])
        self.assertEqual(question.tags.count(), 3)

    def test_answer_create(self):
        question = Question.objects.create(author=self.user1, title='Вопрос1?')
        Answer.objects.create(author=self.user1, question=question, content='Ответ1')
        answer = Answer.objects.get(content='Ответ1')
        self.assertTrue(answer.author, self.user1)
        self.assertEqual(answer.question, question)
        self.assertEqual(answer.content, 'Ответ1')
        self.assertTrue(answer.created_at)

    def test_question_has_answer(self):
        question = Question.objects.create(author=self.user1, title='Заголовок вопроса?', content='Тело вопроса.')
        question.answers.create(author=self.user1, content='Ответ1')
        self.assertFalse(question.has_answer)
        question.answers.create(author=self.user1, content='Ответ2', is_right=True)
        self.assertTrue(question.has_answer)

    def test_question_votes_sum(self):
        question = Question.objects.create(author=self.user1, title='Заголовок вопроса?', content='Тело вопроса.')
        self.assertEqual(question.votes_sum, 0)
        question.votes.create(value=1, user=User.objects.get(pk=2))
        question.votes.create(value=-1, user=User.objects.get(pk=3))
        question.votes.create(value=1, user=User.objects.get(pk=4))
        question.votes.create(value=1, user=User.objects.get(pk=5))
        question.votes.create(value=1, user=User.objects.get(pk=6))
        self.assertEqual(question.votes_sum, 3)

    def test_answer_votes_sum(self):
        question = Question.objects.create(author=self.user1, title='Заголовок вопроса?', content='Тело вопроса.')
        answer = question.answers.create(author=self.user1, content='Ответ')
        self.assertEqual(answer.votes_sum, 0)
        answer.votes.create(value=1, user=User.objects.get(pk=2))
        answer.votes.create(value=-1, user=User.objects.get(pk=3))
        answer.votes.create(value=1, user=User.objects.get(pk=4))
        answer.votes.create(value=1, user=User.objects.get(pk=5))
        answer.votes.create(value=1, user=User.objects.get(pk=6))
        self.assertEqual(answer.votes_sum, 3)

    def test_question_get_last(self):
        question = Question.objects.create(author=self.user1, title='Заголовок вопроса1?', content='Тело вопроса.')
        question.answers.create(author=self.user2, content='Ответ1')
        question = Question.objects.create(author=self.user2, title='Заголовок вопроса2?', content='Тело вопроса.')
        question.answers.create(author=self.user3, content='Ответ1')
        question.answers.create(author=self.user2, content='Ответ2')
        question.answers.create(author=self.user4, content='Ответ3')
        question = Question.objects.create(author=self.user3, title='Заголовок вопроса3?', content='Тело вопроса.')
        question.answers.create(author=self.user5, content='Ответ1')
        question.answers.create(author=self.user3, content='Ответ2')
        question = Question.objects.create(author=self.user4, title='Заголовок вопроса4?', content='Тело вопроса.')
        question = Question.objects.create(author=self.user5, title='Заголовок вопроса5?', content='Тело вопроса.')
        question.answers.create(author=self.user4, content='Ответ1')
        last = Question.get_last()
        self.assertEqual(last[0].title, 'Заголовок вопроса5?')
        self.assertEqual(last[1].title, 'Заголовок вопроса4?')
        self.assertEqual(last[2].title, 'Заголовок вопроса3?')
        self.assertEqual(last[3].title, 'Заголовок вопроса2?')
        self.assertEqual(last[4].title, 'Заголовок вопроса1?')
        self.assertEqual(last[0].count_answers, 1)
        self.assertEqual(last[1].count_answers, 0)
        self.assertEqual(last[2].count_answers, 2)
        self.assertEqual(last[3].count_answers, 3)
        self.assertEqual(last[4].count_answers, 1)

    def test_question_get_hot(self):
        question = Question.objects.create(author=self.user1, title='Заголовок вопроса1?', content='Тело вопроса.')
        question.answers.create(author=self.user2, content='Ответ1')
        question = Question.objects.create(author=self.user2, title='Заголовок вопроса2?', content='Тело вопроса.')
        question.answers.create(author=self.user3, content='Ответ1')
        question.answers.create(author=self.user2, content='Ответ2')
        question.answers.create(author=self.user4, content='Ответ3')
        question = Question.objects.create(author=self.user3, title='Заголовок вопроса3?', content='Тело вопроса.')
        question.answers.create(author=self.user5, content='Ответ1')
        question.answers.create(author=self.user3, content='Ответ2')
        question = Question.objects.create(author=self.user4, title='Заголовок вопроса4?', content='Тело вопроса.')
        question = Question.objects.create(author=self.user5, title='Заголовок вопроса5?', content='Тело вопроса.')
        question.answers.create(author=self.user4, content='Ответ1')
        last = Question.get_hot()
        self.assertEqual(last[0].title, 'Заголовок вопроса2?')
        self.assertEqual(last[1].title, 'Заголовок вопроса3?')
        self.assertEqual(last[2].title, 'Заголовок вопроса5?')
        self.assertEqual(last[3].title, 'Заголовок вопроса1?')
        self.assertEqual(last[4].title, 'Заголовок вопроса4?')
        self.assertEqual(last[0].count_answers, 3)
        self.assertEqual(last[1].count_answers, 2)
        self.assertEqual(last[2].count_answers, 1)
        self.assertEqual(last[3].count_answers, 1)
        self.assertEqual(last[4].count_answers, 0)

    def test_question_get_trending(self):
        question = Question.objects.create(author=self.user1, title='Заголовок вопроса1?', content='Тело вопроса.')
        question.votes.create(user=self.user2, value=1)
        question.votes.create(user=self.user3, value=1)
        question.votes.create(user=self.user5, value=1)
        question = Question.objects.create(author=self.user2, title='Заголовок вопроса2?', content='Тело вопроса.')
        question.votes.create(user=self.user3, value=1)
        question.votes.create(user=self.user2, value=-1)
        question.votes.create(user=self.user4, value=1)
        question = Question.objects.create(author=self.user3, title='Заголовок вопроса3?', content='Тело вопроса.')
        question.votes.create(user=self.user5, value=-1)
        question.votes.create(user=self.user3, value=-1)
        question = Question.objects.create(author=self.user4, title='Заголовок вопроса4?', content='Тело вопроса.')
        question = Question.objects.create(author=self.user5, title='Заголовок вопроса5?', content='Тело вопроса.')
        question.votes.create(user=self.user4, value=-1)
        last = Question.get_trending()
        self.assertEqual(last[0].title, 'Заголовок вопроса2?')
        self.assertEqual(last[1].title, 'Заголовок вопроса1?')
        self.assertEqual(last[2].title, 'Заголовок вопроса3?')
        self.assertEqual(last[3].title, 'Заголовок вопроса5?')
        self.assertEqual(last[4].title, 'Заголовок вопроса4?')
        self.assertEqual(last[0].count_votes, 3)
        self.assertEqual(last[1].count_votes, 3)
        self.assertEqual(last[2].count_votes, 2)
        self.assertEqual(last[3].count_votes, 1)
        self.assertEqual(last[4].count_votes, 0)

    def test_question_search(self):
        Question.objects.create(author=self.user1, title='Заголовок вопроса1: коптер?',
                                content='Тело вопроса. Слова для проверки работы поиска: '
                                        'квадрокоптер, квадро, коптерка.')
        Question.objects.create(author=self.user1, title='Заголовок вопроса2: дрынолет?',
                                content='Тело вопроса. Слова для проверки работы поиска: '
                                        'мама мыла раму.')
        Question.objects.create(author=self.user1, title='Заголовок вопроса3: Коптерка?',
                                content='Тело вопроса. Слова для проверки работы поиска: '
                                        'рама мыла маму.')
        Question.objects.create(author=self.user1, title='Заголовок вопроса4: каптерка?',
                                content='Тело вопроса. Слова для проверки работы поиска: '
                                        'квадратное уравнение.')
        Question.objects.create(author=self.user1, title='Заголов вопроса5: Ёлка?',
                                content='Тело вопроса. Слова для проверки работы поиска: '
                                        'квадрицепцы и бицепцы')
        self.assertEqual(Question.search('коптер').count(), 2)
        self.assertEqual(Question.search('КОПТЕР').count(), 2)
        self.assertEqual(Question.search('Заголовок').count(), 4)
        self.assertEqual(Question.search('квадро').count(), 1)
        self.assertEqual(Question.search('квадр').count(), 3)
        self.assertEqual(Question.search('цепцы').count(), 1)
        self.assertEqual(Question.search('мама').count(), 1)
        self.assertEqual(Question.search('мам').count(), 2)

    def test_question_get_by_tag(self):
        tag1 = Tag.objects.create(name='тег1')
        tag2 = Tag.objects.create(name='Тег2')
        tag3 = Tag.objects.create(name='ТЕГ3')
        tag4 = Tag.objects.create(name='тег4')
        tag5 = Tag.objects.create(name='тег5')
        tag6 = Tag.objects.create(name='тег6')
        question = Question.objects.create(author=self.user1, title='Заголовок1', content='Тело вопроса.')
        question.tags.add(tag1, tag2, tag3)
        question = Question.objects.create(author=self.user1, title='Заголовок2', content='Тело вопроса.')
        question.tags.add(tag1, tag5)
        question = Question.objects.create(author=self.user1, title='Заголовок3', content='Тело вопроса.')
        question.tags.add(tag4, tag2)
        question = Question.objects.create(author=self.user1, title='Заголовок4', content='Тело вопроса.')
        question = Question.objects.create(author=self.user1, title='Заголовок5', content='Тело вопроса.')
        question.tags.add(tag3)
        self.assertEqual(Question.get_by_tag('тег1').count(), 2)
        self.assertEqual(Question.get_by_tag('ТЕГ1').count(), 2)
        self.assertEqual(Question.get_by_tag('тег2').count(), 2)
        self.assertEqual(Question.get_by_tag('тег3').count(), 2)
        self.assertEqual(Question.get_by_tag('тег4').count(), 1)
        self.assertEqual(Question.get_by_tag('тег5').count(), 1)
        self.assertEqual(Question.get_by_tag('тег6').count(), 0)
        self.assertEqual(Question.get_by_tag('тег7').count(), 0)
        self.assertEqual(Question.get_by_tag('тег').count(), 0)

    # def test_registration_and_login(self):
    #     self.client.logout()
    #     username = 'testuser100'
    #     password = 'MBV5z7UhDZ'
    #     response = self.client.post('/registration', {'username': username,
    #                                                   'password1': password,
    #                                                   'password2': password})
    #     self.assertRedirects(response, '/registration_success')
    #     self.assertTrue(User.objects.get(username=username))
    #     response = self.client.post('/login', {'username': username,
    #                                            'password': password})
    #     # print(response.content)
    #     self.assertRedirects(response, '/accounts')

    def test_question_vote(self):
        question = Question.objects.create(author=self.user1, title='Заголовок1', content='Тело вопроса.')
        Vote.vote(question, self.user2, 1)
        self.assertEqual(question.votes_sum, 1)
        Vote.vote(question, self.user3, 1)
        self.assertEqual(question.votes_sum, 2)
        Vote.vote(question, self.user2, 1)
        self.assertEqual(question.votes_sum, 2)
        Vote.vote(question, self.user2, -1)
        self.assertEqual(question.votes_sum, 0)
        Vote.vote(question, self.user4, 1)
        self.assertEqual(question.votes_sum, 1)
        Vote.vote(question, self.user5, -1)
        self.assertEqual(question.votes_sum, 0)

    def test_answer_vote(self):
        question = Question.objects.create(author=self.user1, title='Заголовок1', content='Тело вопроса.')
        answer = Answer.objects.create(author=self.user1, question=question, content='Ответ')
        Vote.vote(answer, self.user2, 1)
        self.assertEqual(answer.votes_sum, 1)
        Vote.vote(answer, self.user3, 1)
        self.assertEqual(answer.votes_sum, 2)
        Vote.vote(answer, self.user2, 1)
        self.assertEqual(answer.votes_sum, 2)
        Vote.vote(answer, self.user2, -1)
        self.assertEqual(answer.votes_sum, 0)
        Vote.vote(answer, self.user4, 1)
        self.assertEqual(answer.votes_sum, 1)
        Vote.vote(answer, self.user5, -1)
        self.assertEqual(answer.votes_sum, 0)

    # def test_login(self):
    #     user = User.objects.create(username=self.username, password=self.password)
    #     user.save()
    #     print(user)
    #     u = User.objects.get(username=self.username)
    #     print(u)
    #     response = self.client.post('/login', {'username': self.username,
    #                                            'password': self.password})
    #     print(response.content)
    #     self.assertRedirects(response, '/accounts')

    # def test_logout(self):
    #     self.client.login(username=self.username, password=self.password)
    #     response = self.client.get('/logout')
    #     self.assertRedirects(self.client.get('/accounts/profile/'), '/login?next=/accounts/profile/')

    # def test_question_create(self):
    #     tags = Tag.objects.filter()[:0]
    #     self.login()
    #     response = self.client.post('/question/new', {'title': 'Тестовый вопрос?',
    #                                        'content': 'Содержание вопроса',
    #                                        'tags': tags})
    #     # print(response)
    #     print(response.content.decode('utf-8'))
    #     question = Question.objects.get(title='Тестовый вопрос?')
    #     # print(question)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRegexpMatches(response.url, '/question/[0-9]+')
    #     response = self.client.get(response.url)
    #     self.assertRegex(response.content.decode('utf-8'), 'Тестовый вопрос?')
    #     self.assertRegex(response.content.decode('utf-8'), 'Содержание вопроса')
