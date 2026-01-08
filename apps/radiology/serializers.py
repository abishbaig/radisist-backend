from rest_framework import serializers
from .models import Scan, Report
from apps.users.serializers import UserSerializer # Assuming this exists, or we use a simple user representation

class ReportSerializer(serializers.ModelSerializer):
    radiologist_name = serializers.CharField(source='radiologist.user.full_name', read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'scan', 'radiologist', 'radiologist_name', 'content', 'impression', 'is_final', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'radiologist']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        # If user is a Patient (and not the radiologist/admin), hide the full content unless it's final?
        # User requirement: "summarized report to user" (impression) and "full and editable report to radiologist" (content)
        
        if request and hasattr(request.user, 'role') and request.user.role == 'PATIENT':
            # Remove full content, only show impression (summary)
            representation.pop('content', None)
        
        return representation

    def create(self, validated_data):
        # Assign current user's radiologist profile if available
        request = self.context.get('request')
        if request and hasattr(request.user, 'radiologist'):
            validated_data['radiologist'] = request.user.radiologist
        return super().create(validated_data)


class ScanSerializer(serializers.ModelSerializer):
    report = ReportSerializer(read_only=True)
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    
    class Meta:
        model = Scan
        fields = [
            'id', 'patient', 'patient_name', 'image', 'scan_type', 'title', 'description', 'created_at',
            'ai_generated', 'ai_predicted_class', 'ai_confidence', 'ai_benign_prob', 'ai_malignant_prob',
            'report'
        ]
        read_only_fields = [
            'id', 'created_at', 'patient', 
            'ai_generated', 'ai_predicted_class', 'ai_confidence', 'ai_benign_prob', 'ai_malignant_prob'
        ]

    def create(self, validated_data):
        # Assign current user's patient profile if available
        request = self.context.get('request')
        if request and hasattr(request.user, 'patient'):
            validated_data['patient'] = request.user.patient
        return super().create(validated_data)
