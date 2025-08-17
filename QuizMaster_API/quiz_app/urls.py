from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import QuizViewSet, QuestionViewSet, ChoiceViewSet, QuizSubmissionViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'choices', ChoiceViewSet)
router.register(r'submissions', QuizSubmissionViewSet)
router.register(r'answers', AnswerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
