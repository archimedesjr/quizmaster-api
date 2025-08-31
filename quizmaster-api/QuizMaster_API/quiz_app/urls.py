from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import QuizViewSet, QuestionViewSet, ChoiceViewSet, QuizSubmissionViewSet, BulkAddViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'choices', ChoiceViewSet, basename='choice')
router.register(r'submissions', QuizSubmissionViewSet, basename='submission')
router.register(r'bulk', BulkAddViewSet, basename="bulk")  # ✅ handles /quizzes/<id>/bulk_add/

urlpatterns = [
    path('', include(router.urls)),
    
    # ✅ JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
