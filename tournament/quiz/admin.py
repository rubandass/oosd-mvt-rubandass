from django.contrib import admin
from quiz.models import Tournament, UserTournament, Category, User

class Admin(admin.ModelAdmin):
    pass

admin.site.register(User, Admin)
admin.site.register(Category, Admin)
admin.site.register(Tournament, Admin)
admin.site.register(UserTournament, Admin)