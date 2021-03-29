# from django.contrib import admin

# from django.db.models import Q


# from . import models

# @admin.register(models.Quiz)
# class QuizAdmin(admin.ModelAdmin):
# 	search_fields = ['code']
# 	list_display=['id', 'name', 'code', 'created_at']
# 	# list_filter = ['author']

# class AnswerInline(admin.TabularInline):
# 	model = models.Answer

# class QuizQuestionFilter(admin.SimpleListFilter):
# 	title = 'quiz'
# 	parameter_name = 'quiz'

# 	def lookups(self, request, model_admin): # create clickable links on right hand side 
# 		quizzes = models.Quiz.objects.all()
# 		lookups = ()
# 		for quiz in quizzes:
# 			lookups += ((quiz.name, quiz.name),)
# 		return lookups

# 	def queryset(self, request, queryset): # return all the ojbects that fit parameter that we set
# 		if self.value(): # why is self.value() containing the year?
# 			quiz_name = self.value()
# 			return queryset.filter(Q(quiz__name=quiz_name))

# @admin.register(models.Question)
# class QuestionAdmin(admin.ModelAdmin):
# 	fields = [
# 		'question',
# 		'quiz',
# 	]
# 	list_display=['id', 'question', 'quiz']
# 	list_filter=[QuizQuestionFilter, ]
# 	search_fields=['code']
# 	inlines = [AnswerInline, ]

# # class AnswerQuestionFilter(admin.SimpleListFilter):
# # 	name = 'quiz'
# # 	parameter_name = 'quiz'

# # 	def lookups(self, request, model_admin): # create clickable links on right hand side 
# # 		quizzes = models.Quiz.objects.all()
# # 		lookups = ()
# # 		for quiz in quizzes:
# # 			lookups += ((quiz.title, quiz.title),)
# # 		return lookups

# # 	def queryset(self, request, queryset): # return all the ojbects that fit parameter that we set
# # 		if self.value(): # why is self.value() containing the year?
# # 			quiz_name = self.value()
# # 			return queryset.filter(Q(question__quiz__name=quiz_name))

# @admin.register(models.Answer)
# class AnswerAdmin(admin.ModelAdmin):
# 	list_display=['text', 'correct_answer', 'question']
# 	# list_filter=[AnswerQuestionFilter, ]

# @admin.register(models.CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
# 	list_display=['id', 'username', 'email', 'first_name', 'last_name']

# admin.site.register(models.UserQuizAnswer)
# admin.site.register(models.UserQuizResult)



from django.contrib import admin
import nested_admin
from .models import Quiz, Question, Answer, QuizTaker, UsersAnswer
from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import User


class UserAdmin(UserAdmin):
	add_form = UserCreationForm
	form = UserChangeForm
	model = User
	list_display = ('username', 'name', 'email', 'is_active')
	list_filter = ('username', 'name', 'email', 'is_active')
	fieldsets = (
		(None, {'fields': ('name', 'username', 'email', 'password')}),
		('Permissions', {'fields': ('is_staff', 'is_active')})
	)
	search_fields = ('username',)
	ordering = ('username',)


admin.site.register(User, UserAdmin)


class AnswerInline(nested_admin.NestedTabularInline):
	model = Answer
	extra = 4
	max_num = 4


class QuestionInline(nested_admin.NestedTabularInline):
	model = Question
	inlines = [AnswerInline,]
	extra = 5


class QuizAdmin(nested_admin.NestedModelAdmin):
	inlines = [QuestionInline,]


class UsersAnswerInline(admin.TabularInline):
	model = UsersAnswer


class QuizTakerAdmin(admin.ModelAdmin):
	inlines = [UsersAnswerInline,]


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuizTaker, QuizTakerAdmin)
admin.site.register(UsersAnswer)

