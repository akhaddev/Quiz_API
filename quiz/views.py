from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import filters
from rest_framework.decorators import action
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics, permissions, mixins
from django.core.exceptions import ImproperlyConfigured
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import get_and_authenticate_user, create_user_account
from rest_framework import status
from django.contrib.auth import get_user_model, logout, login
from .pagination import CustomPagination
import coreapi
from rest_framework.schemas import AutoSchema


User = get_user_model()


class QuizListViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() in ['post', 'put']:
            extra_fields = [
                coreapi.Field('desc')
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class MyQuizListApi(generics.ListAPIView):
    schema = QuizListViewSchema()

    queryset = Quiz.objects.all()
    serializer_class = MyQuizListSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code',]

    def get_queryset(self, *args, **kwargs):
        quiz = Quiz.objects.filter(quiztaker__user=self.request.user)
        return quiz

class QuizListAPI(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizListSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code',]

    schema = QuizListViewSchema()

class QuizDetailAPI(generics.RetrieveAPIView):
    schema = QuizListViewSchema()

    serializer_class = QuizDetailSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, *args, **kwargs):
        slug = self.kwargs["slug"]
        quiz = get_object_or_404(Quiz, slug=slug)
        last_question = None
        obj, created = QuizTaker.objects.get_or_create(user=self.request.user, quiz=quiz)
        if created:
            for question in Question.objects.filter(quiz=quiz):
                UsersAnswer.objects.create(quiz_taker=obj, question=question)
        else:
            last_question = UsersAnswer.objects.filter(quiz_taker=obj, answer__isnull=False)
            if last_question.count() > 0:
                last_question = last_question.last().question.id
            else:
                last_question = None

        return Response({'quiz': self.get_serializer(quiz, context={'request': self.request}).data, 'last_question_id': last_question})


class SaveUsersAnswer(generics.UpdateAPIView):
    serializer_class = UsersAnswerSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def patch(self, request, *args, **kwargs):
        quiztaker_id = request.data['quiztaker']
        question_id = request.data['question']
        answer_id = request.data['answer']

        quiztaker = get_object_or_404(QuizTaker, id=quiztaker_id)
        question = get_object_or_404(Question, id=question_id)
        answer = get_object_or_404(Answer, id=answer_id)

        if quiztaker.completed:
            return Response({
                "message": "This quiz is already complete. you can't answer any more questions"},
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        obj = get_object_or_404(UsersAnswer, quiz_taker=quiztaker, question=question)
        obj.answer = answer
        obj.save()

        return Response(self.get_serializer(obj).data)


class SubmitQuizAPI(generics.GenericAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request, *args, **kwargs):
        quiztaker_id = request.data['quiztaker']
        question_id = request.data['question']
        answer_id = request.data['answer']

        quiztaker = get_object_or_404(QuizTaker, id=quiztaker_id)
        question = get_object_or_404(Question, id=question_id)

        quiz = Quiz.objects.get(slug=self.kwargs['slug'])

        if quiztaker.completed:
            return Response({
                "message": "This quiz is already complete. You can't submit again"},
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        if answer_id is not None:
            answer = get_object_or_404(Answer, id=answer_id)
            obj = get_object_or_404(UsersAnswer, quiz_taker=quiztaker, question=question)
            obj.answer = answer
            obj.save()

        quiztaker.completed = True
        correct_answers = 0

        for users_answer in UsersAnswer.objects.filter(quiz_taker=quiztaker):
            answer = Answer.objects.get(question=users_answer.question, is_correct=True)
            if users_answer.answer == answer:
                correct_answers += 1

        quiztaker.score = int(correct_answers / quiztaker.quiz.question_set.count() * 100)
        quiztaker.save()

        return Response(self.get_serializer(quiz).data)



class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = EmptySerializer
    queryset = ''
    serializer_classes = {
        'login': UserLoginSerializer,
        'register': UserRegisterSerializer
    }

    @action(methods=['POST', ], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['POST', ], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(**serializer.validated_data)
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        logout(request)
        data = {'success': 'Sucessfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class reset_password(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        alldatas={}
        
        if serializer.is_valid(raise_exception=True):
            mname=serializer.save()
            alldatas['data'] = 'successfully registered'
            return Response(alldatas)
        return Response('failed retry after some time')



