# connect urls with views
from django.urls import path
from .views import profile_view, edit_biography_view

'''
Using pk instead of username is more of convension. You might need to update the import if you use viewset or apiview.
path('<str:pk>/', profile_view, name='profile'),
'''
urlpatterns = [
    path('<str:username>/', profile_view, name='profile'),
    path('edit/', edit_biography_view, name='edit_biography'),
]

# http://localhost:8000/profile/laura/ GET 
# http://localhost:8000/profile/edit/ POST 

# {
#     "biography": "Some description of me."
# }