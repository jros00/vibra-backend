from django.shortcuts import render

# Create your views here. Define what is going to happen if someone requests something.

# Implement here the numbers of likes showing on profile

#Implement 2 diff functions: 1 retrieve (get the return) and 1 list function (return all the liked songs, and sort by most recently liked)

from django.shortcuts import render, get_object_or_404
from .models import Profile

# Displaying the profile page and liked tracks
def profile_view(request, username):
    user_profile = get_object_or_404(Profile, user__username=username)
    liked_tracks = user_profile.user.liked_tracks.all().order_by('-liked_date')
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'liked_tracks': liked_tracks,
        'followers_count': user_profile.followers_count(),
        'following_count': user_profile.following_count(),
    })

# Handling the biography edit
def edit_biography_view(request):
    if request.method == 'POST':
        bio = request.POST.get('biography')
        request.user.profile.biography = bio
        request.user.profile.save()
    return render(request, 'edit_profile.html', {'profile': request.user.profile})