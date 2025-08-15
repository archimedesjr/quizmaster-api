from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizSubmission, Answer

class QuizSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quiz
        fields = ['id','title','description', 'created_by', 'created_at'] # include all the Quiz fields


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['id','quiz','text'] # include all the questions fields


class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        fields = ['id','question','text', 'is_correct'] # include all the choice fields


class QuizSubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuizSubmission
        fields = ['id','user','quiz', 'score', 'submitted_at'] # include all the quizsubmission fields


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['id','submission','question', 'selected_choice'] # include all the choice fields