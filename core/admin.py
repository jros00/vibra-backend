from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from core.models import UserActivity, Artist, VisualContent, ContentView, SongView, Track, AudioFeature

# Register your models here.
admin.site.unregister(User)  # Unregister default User
admin.site.register(User, DefaultUserAdmin)  # Re-register with custom settings
admin.site.register(UserActivity)
admin.site.register(Artist)
admin.site.register(VisualContent)
admin.site.register(ContentView)
admin.site.register(SongView)
admin.site.register(Track)
admin.site.register(AudioFeature)