from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin',          'Admin'),
        ('receptionist',   'Receptionist'),
        ('lab_technician', 'Lab Technician'),
        ('patient',        'Patient'),
    )
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionist')
    phone      = models.CharField(max_length=15, blank=True)
    patient_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def is_admin_role(self):
        return self.role == 'admin'

    def is_lab_tech(self):
        return self.role == 'lab_technician'

    def is_receptionist(self):
        return self.role == 'receptionist'

    def is_patient_role(self):
        return self.role == 'patient'
