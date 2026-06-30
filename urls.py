from django.urls import path
from . import views

urlpatterns = [
    path(
        'attendance/',
        views.take_attendance,
        name='take_attendance'
    ),
]