from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('', views.results_list, name='list'),
    path('<int:pk>/file/', views.download_result_file, name='download_result_file'),
]