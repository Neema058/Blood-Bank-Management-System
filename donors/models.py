from django.db import models
import datetime

BLOOD_GROUPS = (
    ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
    ('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-'),
)
RARE_GROUPS = ['AB-', 'B-', 'O-']

class Donor(models.Model):
    GENDER = (('M','Male'),('F','Female'),('O','Other'))

    donor_id       = models.AutoField(primary_key=True)
    full_name      = models.CharField(max_length=100)
    cnic           = models.CharField(max_length=15, unique=True)
    age            = models.IntegerField()
    gender         = models.CharField(max_length=1, choices=GENDER)
    blood_group    = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    phone          = models.CharField(max_length=15)
    email          = models.EmailField(blank=True)
    address        = models.TextField(blank=True)
    medical_history= models.TextField(blank=True)
    last_donation  = models.DateField(null=True, blank=True)
    is_active      = models.BooleanField(default=True)
    registered_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.blood_group})"

    def is_eligible(self):
        if not self.last_donation:
            return True
        days = (datetime.date.today() - self.last_donation).days
        return days >= 56

    def days_until_eligible(self):
        if not self.last_donation:
            return 0
        days = (datetime.date.today() - self.last_donation).days
        remaining = 56 - days
        return max(0, remaining)

    def is_rare_group(self):
        return self.blood_group in RARE_GROUPS

    @property
    def total_donations(self):
        return self.donation_set.filter(status='accepted').count()
