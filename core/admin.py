from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from core.models import UserPreference, ListeningHistory, Artist, Track, AudioFeature, RequestLog


# Register your models here.
admin.site.unregister(User)  # Unregister default User
admin.site.register(User, DefaultUserAdmin)  # Re-register with custom settings
admin.site.register(Artist)
admin.site.register(Track)
admin.site.register(AudioFeature)
admin.site.register(UserPreference)
admin.site.register(ListeningHistory)
admin.site.register(RequestLog)

