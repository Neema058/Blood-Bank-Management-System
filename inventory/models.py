from django.db import models
import datetime

BLOOD_GROUPS = (
    ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
    ('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-'),
)
RARE_GROUPS = ['AB-', 'B-', 'O-']

class BloodUnit(models.Model):
    STATUS = (
        ('available', 'Available'),
        ('issued',    'Issued'),
        ('expired',   'Expired'),
        ('rejected',  'Rejected'),
    )

    donation       = models.OneToOneField('donations.Donation', on_delete=models.CASCADE, null=True)
    blood_group    = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    collected_date = models.DateField()
    expiry_date    = models.DateField()
    status         = models.CharField(max_length=10, choices=STATUS, default='available')
    issued_to      = models.ForeignKey('blood_requests.BloodRequest', on_delete=models.SET_NULL, null=True, blank=True)
    issued_date    = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Unit #{self.id} - {self.blood_group} ({self.status})"

    def is_expired(self):
        return datetime.date.today() > self.expiry_date

    def days_to_expiry(self):
        delta = self.expiry_date - datetime.date.today()
        return delta.days

    def expiry_status(self):
        days = self.days_to_expiry()
        if days < 0:
            return 'expired'
        elif days <= 7:
            return 'critical'
        elif days <= 14:
            return 'warning'
        return 'good'

    def is_rare(self):
        return self.blood_group in RARE_GROUPS

    @classmethod
    def auto_expire(cls):
        today = datetime.date.today()
        cls.objects.filter(status='available', expiry_date__lt=today).update(status='expired')

    @classmethod
    def stock_by_group(cls):
        result = {}
        for bg, _ in BLOOD_GROUPS:
            result[bg] = cls.objects.filter(blood_group=bg, status='available').count()
        return result
