from django.urls import path
from .views import login
from .views import logout

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]
