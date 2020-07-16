from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Max, Avg
from datetime import date
import json

class Category(models.Model):
    category = models.CharField(max_length=50)
    key = models.IntegerField()

    def __str__(self):
        return self.category

class User(AbstractUser):
  interests = models.ManyToManyField(Category, blank=True, related_name='interested_players')

  @property
  def taken(self):
      return UserTournament.objects.filter(user_id = self.id)

class Tournament(models.Model):
    DIFFICULTY_CHOICES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
    ]

    name = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    questions = models.TextField()

    @property
    def total_taken(self):
        return len(UserTournament.objects.filter(tournament_id=self.id))
    
    @property
    def quiz_questions(self):
        return json.dumps([q['question'] for q in json.loads(self.questions)])
    
    @property
    def taken_by(self):
        return [t.user_id for t in self.tournaments.all()]

    @property
    def high_score(self):
        max = UserTournament.objects.filter(tournament_id=self.id).aggregate(Max('score'))
        return max["score__max"] if max else 0 

    @property
    def average_score(self):
        average = UserTournament.objects.filter(tournament_id=self.id).aggregate(Avg('score'))
        return average['score__avg']

    @property
    def top_players(self):
        return json.dumps([{"player":t.user.username,"score":t.score,"date":t.date_taken.strftime("%b %d %Y")} for t in UserTournament.objects.filter(tournament_id=self.id).order_by('-score')[:5]])

    @staticmethod
    def ongoing():
        return Tournament.objects.filter(start_date__lte=date.today(), end_date__gte=date.today())

    @staticmethod
    def upcoming():
        return Tournament.objects.filter(start_date__gt=date.today())

    @staticmethod
    def past():
        return Tournament.objects.filter(end_date__lt=date.today())

class UserTournament(models.Model):
    user = models.ForeignKey(User,related_name="players", on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament,related_name="tournaments", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    date_taken = models.DateTimeField(auto_now_add=True)
    answers = models.TextField()
