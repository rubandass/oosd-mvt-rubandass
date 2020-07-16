from django.urls import path
from rest_framework import routers
from . import views
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

router = routers.DefaultRouter()
router.register("api/tournament",views.TournamentViewset,"TournamentViewset")

urlpatterns = [
    url(r'^login/', auth_views.LoginView.as_view(template_name="quiz/registration/login.html"), name="login"),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page="login"), name='logout'),
    path('signup', views.signup, name='signup'),

    path('', views.dashboard, name='dashboard'),
    path('tournaments', views.tournaments, name='tournaments'),
    path('quiz/<int:id>/', views.quiz, name='quiz'),
    path('results/<int:id>/', views.results, name='results'),
]

urlpatterns += router.urls