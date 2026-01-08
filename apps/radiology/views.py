from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Scan, Report
from .serializers import ScanSerializer, ReportSerializer
from apps.users.models import User

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.PATIENT

class IsRadiologist(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.RADIOLOGIST

class ScanViewSet(viewsets.ModelViewSet):
    serializer_class = ScanSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'patient__user__full_name']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.PATIENT:
            return Scan.objects.filter(patient__user=user)
        elif user.role == User.RADIOLOGIST:
            return Scan.objects.all() # Radiologists see all scans
        elif user.role == User.ADMIN or user.is_staff:
            return Scan.objects.all()
        return Scan.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.PATIENT:
            serializer.save(patient=user.patient)
        else:
            # If admin creates, they must specify patient? 
            # For now, let's assume admin creation requires passing patient ID if not caught by serializer logic
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rerun_ai(self, request, pk=None):
        """Manually trigger AI prediction for a scan"""
        scan = self.get_object()
        if not scan.image:
            return Response({'error': 'No image associated with this scan'}, status=status.HTTP_400_BAD_REQUEST)
        
        scan.run_ai_prediction()
        scan.refresh_from_db()
        serializer = self.get_serializer(scan)
        return Response(serializer.data)


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.PATIENT:
            # Patients can only see reports for their scans
            return Report.objects.filter(scan__patient__user=user)
        elif user.role == User.RADIOLOGIST:
            # Radiologists can see all reports, or reports they authored
            return Report.objects.all()
        return Report.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRadiologist()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(radiologist=self.request.user.radiologist)
