from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission
from .models import Quiz, Question, Choice, QuizSubmission, Answer
from .serializers import QuizSerializer, QuestionSerializer, ChoiceSerializer, QuizSubmissionSerializer, AnswerSerializer


# ✅ Custom permission (Teachers can create/edit, Students read-only)
class IsTeacherOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff  # Teachers must be staff


# ✅ Quiz CRUD
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set created_by as the logged-in teacher
        serializer.save(created_by=self.request.user)


# ✅ Question CRUD
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]


# ✅ Choice CRUD
class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]


# ✅ Submissions
class QuizSubmissionViewSet(viewsets.ModelViewSet):
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def submit_quiz(self, request, pk=None):
        """
        Endpoint: POST /quizzes/<id>/submit_quiz/
        Allows a student to submit answers for a quiz.
        """
        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        # Prevent duplicate submissions
        if QuizSubmission.objects.filter(user=user, quiz=quiz).exists():
            return Response({"error": "You have already submitted this quiz."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Prevent teachers from submitting their own quiz
        if quiz.created_by == user:
            return Response({"error": "Teachers cannot take their own quiz."},
                            status=status.HTTP_403_FORBIDDEN)

        answers = request.data.get("answers", [])
        if not answers:
            return Response({"error": "No answers provided."},
                            status=status.HTTP_400_BAD_REQUEST)

        submission = QuizSubmission.objects.create(user=user, quiz=quiz, score=0)
        score = 0
        total_questions = quiz.question_set.count()

        for ans in answers:
            try:
                question = Question.objects.get(id=ans["question"], quiz=quiz)
                choice = Choice.objects.get(id=ans["selected_choice"], question=question)
            except (Question.DoesNotExist, Choice.DoesNotExist, KeyError):
                return Response({"error": f"Invalid answer data: {ans}"},
                                status=status.HTTP_400_BAD_REQUEST)

            Answer.objects.create(submission=submission, question=question, selected_choice=choice)

            if choice.is_correct:
                score += 1

        submission.score = score
        submission.save()

        return Response({
            "message": "Quiz submitted successfully",
            "score": score,
            "total_questions": total_questions,
            "percentage": round((score / total_questions) * 100, 2) if total_questions > 0 else 0
        })


    # ✅ Extra: Get all submissions of the logged-in user
    @action(detail=False, methods=["get"])
    def my_submissions(self, request):
        submissions = QuizSubmission.objects.filter(user=request.user)
        serializer = QuizSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    # ✅ Extra: Teacher can view submissions for their quiz
    @action(detail=True, methods=["get"])
    def quiz_submissions(self, request, pk=None):
        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        if quiz.created_by != request.user:
            return Response({"error": "You are not allowed to view submissions for this quiz."},
                            status=status.HTTP_403_FORBIDDEN)

        submissions = QuizSubmission.objects.filter(quiz=quiz)
        serializer = QuizSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


# ✅ Bulk add questions & choices
class BulkAddViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

    @action(detail=True, methods=["post"])
    def bulk_add(self, request, pk=None):
        """
        Endpoint: POST /quizzes/<id>/bulk_add/
        Allows a teacher to bulk add questions & choices to a quiz.
        """
        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only quiz creator can bulk add
        if quiz.created_by != request.user:
            return Response({"error": "You can only add questions to quizzes you created."},
                            status=status.HTTP_403_FORBIDDEN)

        questions_data = request.data.get("questions", [])
        if not questions_data:
            return Response({"error": "No questions provided"}, status=status.HTTP_400_BAD_REQUEST)

        for q in questions_data:
            if not q.get("choices"):
                return Response({"error": "Each question must have at least one choice."},
                                status=status.HTTP_400_BAD_REQUEST)

            question = Question.objects.create(quiz=quiz, text=q["text"])

            for c in q["choices"]:
                Choice.objects.create(
                    question=question,
                    text=c["text"],
                    is_correct=c.get("is_correct", False)
                )

        return Response({"message": "Questions and choices added successfully"})
