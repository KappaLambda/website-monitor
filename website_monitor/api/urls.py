from django.urls import path

from api import views

urlpatterns = [
    path(
        '',
        views.HomeView.as_view(),
        name='home',
    ),
    path(
        'check-tasks/',
        views.CheckTaskList.as_view(),
        name='check-tasks',
    ),
    path(
        'check-tasks/<int:pk>/',
        views.CheckTaskDetails.as_view(),
        name='check-task',
    ),
    path(
        'check-tasks/<int:pk>/results/',
        views.CheckTaskResultList.as_view(),
        name='check-task-results',
    ),
]
