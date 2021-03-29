from django.urls import path, include, re_path
from rest_framework import routers
from . import views


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'api', views.AuthViewSet, basename='api')


urlpatterns = [
    path('', include(router.urls)),
    path("my-quizzes/", views.MyQuizListApi.as_view()),
	path("quizzes/", views.QuizListAPI.as_view()),
	path("save-answer/", views.SaveUsersAnswer.as_view()),
	re_path(r"quizzes/(?P<slug>[\w\-]+)/$", views.QuizDetailAPI.as_view()),
	re_path(r"quizzes/(?P<slug>[\w\-]+)/submit/$", views.SubmitQuizAPI.as_view()),
    path('reset_password/', views.reset_password.as_view(), name='reset_password'),

    path('api-auth/', include('rest_framework.urls', namespace='rest-framework')),

    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    
]
