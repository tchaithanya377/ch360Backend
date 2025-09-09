from django.http import JsonResponse
from rest_framework import generics, permissions
from .models import OpenRequest, RequestComment
from .serializers import OpenRequestSerializer, RequestCommentSerializer


def health(request):
    return JsonResponse({"status": "ok", "app": "open_requests"})


class OpenRequestListCreateView(generics.ListCreateAPIView):
    queryset = OpenRequest.objects.all()
    serializer_class = OpenRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class OpenRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OpenRequest.objects.all()
    serializer_class = OpenRequestSerializer
    permission_classes = [permissions.IsAuthenticated]


class RequestCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = RequestCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RequestComment.objects.filter(request_id=self.kwargs['request_id']).select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, request_id=self.kwargs['request_id'])

# Create your views here.
