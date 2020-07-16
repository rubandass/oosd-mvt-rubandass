from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse, JsonResponse

from rest_framework import viewsets

from  .models import Tournament,Category,UserTournament,User
from .serializer import TournamentSerializer
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from django.views.generic import CreateView
from django.core import serializers
import json
import random

# user signup
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('/tournaments')
    else:
        form = SignUpForm()
    return render(request, 'quiz/signup_form.html', {'form': form})

# user dashboard
@login_required(login_url='/login/')
def dashboard(request):
    return render(request, 'quiz/dashboard.html', {'tournament_ongoing': Tournament.ongoing(), 'tournament_upcoming': Tournament.upcoming(), 'tournament_past': Tournament.past(), 'average_score': Tournament.average_score})

# questions
def quiz(request, id):
    tournament = Tournament.objects.get(id = id)
    questions = json.loads(tournament.questions)
    for question in questions:
        question['incorrect_answers'].append(question['correct_answer'])
        random.shuffle(question['incorrect_answers'])
    return render(request, 'quiz/quiz.html', {'tournament': tournament,"questions":questions})    

# results
def results(request, id):
    tournament = Tournament.objects.get(id = id)
    questions = json.loads(tournament.questions)
    results = UserTournament.objects.filter(tournament_id=id,user_id=request.user.id)
    if request.method == "POST" and not results:
        total = 0
        for i in range(1,10):
            user_answer = request.POST.get(str(i), None)
            if user_answer == questions[i-1]['correct_answer']:
                total += 1
            questions[i-1]["user_answer"] = user_answer
        results = UserTournament.objects.create(tournament_id=id,user_id=request.user.id,score=total,answers=json.dumps(questions))
        return redirect(f'/results/{id}')
    else:
        answers = []
        if results:
            results = results[0]
            answers = json.loads(results.answers)
        return render(request, 'quiz/results.html',{"results":results,"answers":answers})    

# tournaments and categories
def tournaments(request):
    tournaments = Tournament.objects.all()
    categories = Category.objects.all()
    return render(request, 'quiz/tournaments.html', {'tournaments':tournaments, 'categories':categories})	


class TournamentViewset(viewsets.ModelViewSet):
    serializer_class = TournamentSerializer
    def get_queryset(self):
        return Tournament.objects.all()

    def perform_create(self, serializer):
        serializer.save()


