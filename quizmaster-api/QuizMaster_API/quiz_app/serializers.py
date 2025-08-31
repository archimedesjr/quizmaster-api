from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizSubmission, Answer

# -------------------- CHOICE --------------------
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']
        extra_kwargs = {
            'is_correct': {'write_only': True}  # Students shouldn’t see correct answers when fetching quiz
        }

# -------------------- QUESTION --------------------
class QuestionSerializer(serializers.ModelSerializer):
    # Nest choices for GET
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'choices']

# -------------------- QUIZ --------------------
class QuizSerializer(serializers.ModelSerializer):
    # Include questions (with choices)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 'questions']
        read_only_fields = ['created_by', 'created_at']

# -------------------- ANSWER --------------------
class AnswerSerializer(serializers.ModelSerializer):
    # Show related details for GET
    question_text = serializers.CharField(source='question.text', read_only=True)
    selected_choice_text = serializers.CharField(source='selected_choice.text', read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'submission', 'question', 'selected_choice', 
                  'question_text', 'selected_choice_text']

# -------------------- QUIZ SUBMISSION --------------------
class QuizSubmissionSerializer(serializers.ModelSerializer):
    # Nested answers
    answers = AnswerSerializer(many=True, read_only=True)

    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizSubmission
        fields = ['id', 'user', 'quiz', 'quiz_title', 'score', 'submitted_at', 'answers']
        read_only_fields = ['score', 'submitted_at']
