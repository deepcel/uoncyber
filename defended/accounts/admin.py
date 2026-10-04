from django.contrib import admin
from .models import Profile, LoginAttempt

admin.site.register(Profile)
admin.site.register(LoginAttempt)