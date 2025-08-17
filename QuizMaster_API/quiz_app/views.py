from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from .models import Quiz, Question, QuizSubmission, Choice, Answer
from .serializers import QuizSerializer, QuestionSerializer, ChoiceSerializer, QuizSubmissionSerializer, AnswerSerializer

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    @action(detail=True, methods=['post'])
    def submit_quiz(self, request, pk=None):
        quiz = self.get_object()   # Get the quiz the user is submitting
        user = request.user        # Get the logged-in user

        # The client must send answers as: { "answers": [{ "question": id, "choice": id }, ...] }
        answers_data = request.data.get("answers", [])
        if not answers_data:
            return Response({"error": "No answers provided."}, status=status.HTTP_400_BAD_REQUEST)

        score = 0
        total_questions = quiz.question_set.count()

        # Create a new submission record
        submission = QuizSubmission.objects.create(user=user, quiz=quiz, score=0)

        # Loop through the submitted answers
        for ans in answers_data:
            try:
                question = Question.objects.get(id=ans["question"], quiz=quiz)
                choice = Choice.objects.get(id=ans["choice"], question=question)

                # Save each answer
                Answer.objects.create(
                    submission=submission,
                    question=question,
                    selected_choice=choice
                )

                # Check correctness
                if choice.is_correct:
                    score += 1

            except (Question.DoesNotExist, Choice.DoesNotExist):
                continue  # skip invalid data

        # Update submission with final score
        submission.score = score
        submission.save()

        return Response({
            "message": f"Quiz submitted successfully!",
            "score": score,
            "total_questions": total_questions
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def submissions(self, request, pk=None):
        quiz = self.get_object()  # fetch the quiz using the pk in URL

        # ✅ Only the creator of the quiz can view all submissions
        if quiz.created_by != request.user:
            return Response(
                {"error": "You are not allowed to view submissions for this quiz."},
                status=403
            )

        submissions = quiz.quizsubmission_set.all()  # fetch all related submissions
        serializer = QuizSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)
    
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    # ✅ Add multiple questions at once
    @action(detail=True, methods=['post'])
    def bulk_add(self, request, pk=None):
        quiz = self.get_object()
        questions_data = request.data.get('questions', [])

        created = []
        for q in questions_data:
            question = Question.objects.create(quiz=quiz, text=q["text"])
            created.append(question)

        return Response({"message": f"{len(created)} questions added to {quiz.title}"})

class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]

    # ✅ Add multiple choices at once
    @action(detail=True, methods=['post'])
    def bulk_add_choices(self, request, pk=None):
        question = self.get_object()
        choices_data = request.data.get('choices', [])

        created = []
        for c in choices_data:
            choice = Choice.objects.create(
                question=question,
                text=c["text"],
                is_correct=c.get("is_correct", False)
            )
            created.append(choice)

        return Response({"message": f"{len(created)} choices added to question '{question.text}'"})

class QuizSubmissionViewSet(viewsets.ModelViewSet):
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        submissions = QuizSubmission.objects.filter(user=request.user)
        serializer = QuizSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

