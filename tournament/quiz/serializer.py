
from  .models import Tournament,Category,UserTournament,User
from rest_framework import serializers
# from django.contrib.auth.models import User
from requests import get
import json

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"



class TournamentSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    category_id = serializers.PrimaryKeyRelatedField(source="category",queryset=Category.objects.all(),required=False)
    questions = serializers.CharField(required=False)
    class Meta:
        model = Tournament
        fields = "__all__"

    def create(self,validated_data):
        difficulty = validated_data["difficulty"]
        category = validated_data["category"]
        # Call the opentdb api and get the qustions then save it in questions
        url = f'https://opentdb.com/api.php?amount=10&category={category.key}&difficulty={difficulty}&type=multiple'
        response = get(url)
        response_data = response.json()
        tournament = Tournament.objects.create(**validated_data,questions=json.dumps(response_data["results"]))
        return tournament

class UserTournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTournament
        fields = "__all__"