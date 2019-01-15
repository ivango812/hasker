from django.urls import path

from . import views

urlpatterns = [
    path('hot', views.IndexListView.as_view(), name='hot'),
    path('search', views.SearchListView.as_view(), name='search'),
    path('registration', views.UserCreationView.as_view(), name='registration'),
    path('registration_success', views.RegistrationSuccessView.as_view(), name='registration_success'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('logout', views.UserLogoutView.as_view(), name='logout'),
    path('accounts', views.UserProfileView.as_view(), name='account'),
    path('accounts/profile/', views.UserEditView.as_view(), name='profile'),
    path('accounts/myquestions/', views.MyQuestionsListView.as_view(), name='myquestions'),
    path('accounts/myanswers/', views.MyAnswersListView.as_view(), name='myanswers'),
    path('question/new', views.QuestionCreateView.as_view(), name='new_question'),
    path('question/<int:pk>', views.QuestionCreateAnswerView.as_view(), name='question'),
    path('tag/<int:pk>', views.TagDetailView.as_view(), name='tag'),
    path('right_answer/<int:pk>', views.RightAnswerActionView.as_view(), name='right_answer'),
    path('vote/<str:model_entity>/<int:pk>/<str:value_alias>', views.VoteActionView.as_view(), name='vote'),
]