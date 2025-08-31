from django.contrib import admin
from .models import Quiz, Question, QuizSubmission, Choice, Answer
# Register your models here
admin.site.register([Quiz, Question, QuizSubmission, Choice, Answer])