from django.db import models
from patients.models import Patient
from accounts.models import CustomUser

BLOOD_GROUPS = (
    ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
    ('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-'),
)

class BloodRequest(models.Model):
    URGENCY = (
        ('normal',    'Normal'),
        ('urgent',    'Urgent'),
        ('emergency', 'Emergency'),
    )
    STATUS = (
        ('pending',   'Pending'),
        ('approved',  'Approved'),
        ('rejected',  'Rejected'),
        ('fulfilled', 'Fulfilled'),
    )

    patient          = models.ForeignKey(Patient, on_delete=models.CASCADE)
    blood_group      = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_required   = models.IntegerField(default=1)
    urgency          = models.CharField(max_length=10, choices=URGENCY, default='normal')
    status           = models.CharField(max_length=10, choices=STATUS, default='pending')
    request_date     = models.DateTimeField(auto_now_add=True)
    processed_by     = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    notes            = models.TextField(blank=True)
    fulfilled_date   = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"REQ#{self.id} - {self.patient.full_name} ({self.blood_group}) [{self.urgency}]"

    def is_emergency(self):
        return self.urgency == 'emergency'

    class Meta:
        ordering = ['-request_date']
