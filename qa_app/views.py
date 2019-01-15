from django.shortcuts import render
from .models import User, Question, Answer, Tag, Vote
from .forms import QuestionForm, AnswerForm, RegistrationForm, UserForm
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden, HttpResponseNotAllowed
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django import views
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.core.mail import send_mail


class IndexListView(ListView):
    model = Question
    template_name = 'index.html'
    context_object_name = 'last_questions'
    paginate_by = 10

    def get_queryset(self):
        if self.request.path == '/hot':
            return Question.get_hot()
        else:
            return Question.get_last()


class SearchListView(ListView):
    model = Question
    template_name = 'search.html'
    context_object_name = 'found_questions'
    paginate_by = 20

    def get_queryset(self):
        text = str(self.request.GET.get('q')).strip()
        if text.lower().startswith('tag:'):
            tag_name = text[4:].strip()
            try:
                return Question.get_by_tag(tag_name)
            except ObjectDoesNotExist:
                return Question.objects.none()
        else:
            return Question.search(text)


class RegistrationView(CreateView):
    model = User
    fields = ['username', 'password', 'first_name', 'last_name', 'email']
    template_name = 'registration.html'
    success_url = 'registration_success'


class RegistrationSuccessView(TemplateView):
    template_name = 'registration_success.html'


class UserCreationView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration.html'
    success_url = 'registration_success'


class UserLoginView(LoginView):
    template_name = 'login.html'


class UserLogoutView(LogoutView):
    next_page = 'index'


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'account.html'


class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    login_url = 'login'

    template_name = 'question_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('question', kwargs={'pk': self.object.pk})


class QuestionCreateAnswerView(CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'question.html'

    def send_notification(self):
        email_subject = 'New answer from {}'.format(self.object.author)
        email_message = 'You have a new answer from {} on "{}":\r\n' \
                        '\r\n' \
                        '{}\r\n' \
                        '\r\n' \
                        '{}'.format(self.object.author,
                                    self.object.question.title,
                                    self.object.content,
                                    self.request.build_absolute_uri())
        send_mail(email_subject,
                  email_message,
                  'ivan@urlix.ru',
                  [self.object.question.author.email],
                  fail_silently=False)

    def form_valid(self, form):
        self.success_url = str(self.kwargs['pk'])
        form.instance.author = self.request.user
        form_valid_result = super().form_valid(form)
        if form_valid_result and self.object.author.email:
            self.send_notification()
        return form_valid_result

    def get_context_data(self, **kwargs):
        self.initial = {'question': self.kwargs['pk']}
        context = super().get_context_data(**kwargs)
        question = Question.objects.get(pk=self.kwargs['pk'])
        answers = question.get_sorted_answers()
        paginator = Paginator(answers, settings.ANSWERS_PER_PAGE)
        try:
            answers = paginator.get_page(self.request.GET.get('page'))
        except (PageNotAnInteger, KeyError) as e:
            answers = paginator.get_page(1)
        except EmptyPage:
            answers = paginator.get_page(paginator.num_pages)

        context.update({
            'question': question,
            'answers': answers,
            'paginator': paginator,
            'page_obj': answers,
        })
        return context


class TagDetailView(DetailView):
    model = Tag
    template_name = 'tag.html'


class UserProfileEditView(LoginRequiredMixin, views.View):

    context_object_name = 'form_user'
    form_class = UserForm
    template_name = 'profile_form.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        form_user = UserForm(instance=request.user)
        return render(request, self.template_name, {'form_user': form_user})

    def post(self, request, *args, **kwargs):
        form_user = UserForm(instance=request.user, data=request.POST, files=request.FILES)
        if form_user.is_valid():
            form_user.save()
            return HttpResponseRedirect(reverse('account'))
        return render(request, self.template_name, {'form_user': form_user})


class UserEditView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    login_url = 'login'
    template_name = 'profile_form.html'

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)

    def get_success_url(self):
        return reverse('account')


class RightAnswerActionView(LoginRequiredMixin, views.View):
    login_url = 'login'

    def get(self, request, pk):
        try:
            answer = Answer.objects.get(pk=pk)
            if answer.question.author == request.user or request.user.is_superuser:
                # and not answer.question.answers.filter(is_right=True) :
                answer.question.answers.filter(is_right=True).update(is_right=False)
                answer.is_right = True
                answer.save()
                return HttpResponseRedirect(reverse('question', args=(answer.question.pk,)))
            return HttpResponseForbidden('You DO NOT have an access')
        except:
            return HttpResponseNotAllowed('Incorrect request')


class VoteActionView(LoginRequiredMixin, views.View):
    login_url = 'login'

# TODO: refactor vote design
    def get(self, request, model_entity, pk, value_alias):
        if type(pk) is int \
           and type(model_entity) is str and model_entity in ('question', 'answer') \
           and type(value_alias) is str and value_alias in ('like', 'dislike'):
            try:
                value = 1 if value_alias == 'like' else -1
                if model_entity == 'answer':
                    answer = Answer.objects.get(pk=pk)
                    question = answer.question
                    Vote.vote(answer, request.user, value)
                if model_entity == 'question':
                    question = Question.objects.get(pk=pk)
                    Vote.vote(question, request.user, value)
                return HttpResponseRedirect(reverse('question', kwargs={'pk': question.pk}))
            except ObjectDoesNotExist:
                pass
        return HttpResponseNotFound('Incorrect request')


class MyQuestionsListView(ListView):
    model = Question
    paginate_by = 10
    template_name = 'myquestions.html'

    def get_queryset(self):
        return Question.get_by_user(self.request.user)


class MyAnswersListView(ListView):
    model = Answer
    paginate_by = 10
    template_name = 'myanswers.html'

    def get_queryset(self):
        return Answer.get_by_user(self.request.user)
