from django.db import models
from apps.users.models import Patient, Radiologist
from .ai_service import ai_service
import os

class Scan(models.Model):
    SCAN_TYPES = [
        ('MRI', 'MRI'),
        ('CT', 'CT Scan'),
        ('XRAY', 'X-Ray'),
        ('MAMMOGRAM', 'Mammogram'),
        ('OTHER', 'Other'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='scans')
    image = models.ImageField(upload_to='scans/%Y/%m/%d/')
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPES, default='MAMMOGRAM')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # AI Fields
    ai_generated = models.BooleanField(default=False)
    ai_predicted_class = models.CharField(max_length=50, blank=True, null=True)
    ai_confidence = models.FloatField(null=True, blank=True)
    ai_benign_prob = models.FloatField(null=True, blank=True)
    ai_malignant_prob = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.scan_type} for {self.patient} - {self.created_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Trigger AI prediction if it's a new scan and has an image
        if is_new and self.image:
            self.run_ai_prediction()

    def run_ai_prediction(self):
        if not self.image:
            return

        try:
            # Get absolute path for the image
            image_path = self.image.path
            if os.path.exists(image_path):
                print(f"Running AI prediction for scan {self.pk}...")
                result = ai_service.predict(image_path)
                
                if result:
                    self.ai_generated = True
                    self.ai_predicted_class = result['predicted_class']
                    self.ai_confidence = result['confidence']
                    self.ai_benign_prob = result['benign_probability']
                    self.ai_malignant_prob = result['malignant_probability']
                    self.save(update_fields=[
                        'ai_generated', 'ai_predicted_class', 
                        'ai_confidence', 'ai_benign_prob', 'ai_malignant_prob'
                    ])
                    print(f"AI Prediction saved: {result}")
                    
                    # Create or Update Linked Report
                    # We use 'defaults' to set fields only on creation, but maybe we want to overwrite if AI re-runs?
                    # Let's assume re-running AI should update the draft report if it's not final.
                    
                    report_content = (
                        f"Automated AI Analysis:\n"
                        f"- Predicted Diagnosis: {result['predicted_class']}\n"
                        f"- Confidence Level: {result['confidence']}%\n"
                        f"- Malignancy Probability: {result['malignant_probability']}%\n"
                        f"- Benign Probability: {result['benign_probability']}%\n\n"
                        f"This is a preliminary automated finding. Please review."
                    )
                    
                    impression_summary = f"AI Prediction: {result['predicted_class']} ({result['confidence']}%)"

                    report, created = Report.objects.get_or_create(
                        scan=self,
                        defaults={
                            'content': report_content,
                            'impression': impression_summary,
                            'is_final': False
                        }
                    )
                    
                    if not created and not report.is_final:
                        # If report exists and is NOT final, update it with new AI result
                        report.content = report_content
                        report.impression = impression_summary
                        report.save()
            else:
                print(f"Image not found at {image_path}")
        except Exception as e:
            print(f"Failed to run AI prediction: {e}")


class Report(models.Model):
    scan = models.OneToOneField(Scan, on_delete=models.CASCADE, related_name='report')
    radiologist = models.ForeignKey(Radiologist, on_delete=models.SET_NULL, null=True, related_name='reports')
    content = models.TextField(help_text="Full medical report")
    impression = models.TextField(help_text="Summary of findings", blank=True)
    is_final = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report for Scan {self.scan.pk} by {self.radiologist}"
