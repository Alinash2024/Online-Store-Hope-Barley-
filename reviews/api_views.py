"""API views for the reviews app using Django REST Framework."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for listing and managing reviews."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.none()

    def get_queryset(self):
        """Get the queryset for reviews."""
        return Review.objects.all()

    def perform_create(self, serializer):
        """Set the user for the new review."""
        serializer.save(user=self.request.user)
