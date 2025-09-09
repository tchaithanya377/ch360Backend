from django.urls import path
from . import views

app_name = 'open_requests'

urlpatterns = [
    path('health/', views.health, name='health'),
    path('requests/', views.OpenRequestListCreateView.as_view(), name='request-list-create'),
    path('requests/<int:pk>/', views.OpenRequestDetailView.as_view(), name='request-detail'),
    path('requests/<int:request_id>/comments/', views.RequestCommentListCreateView.as_view(), name='request-comments'),
]


