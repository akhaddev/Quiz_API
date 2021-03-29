from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from quiz import views
from rest_framework_simplejwt import views as jwt_views
from rest_framework_swagger.views import get_swagger_view


schema_view = get_swagger_view(title='Quiz App Swagger')

# router = routers.SimpleRouter()
# router.register(r'quizzes', views.QuizViewSet)
# router.register(r'questions', views.QuestionViewSet)
# router.register(r'answers', views.AnswerViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('quiz/', include('quiz.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('', schema_view),
    path('accunts/', include('rest_framework.urls'))
]
