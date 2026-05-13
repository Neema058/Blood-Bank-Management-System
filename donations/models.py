from django.db import models
from donors.models import Donor
from accounts.models import CustomUser
import datetime

class Donation(models.Model):
    TEST_RESULT = (('pass','Pass'),('fail','Fail'))
    STATUS = (('accepted','Accepted'),('rejected','Rejected'))

    donor        = models.ForeignKey(Donor, on_delete=models.CASCADE)
    donation_date= models.DateField()
    volume_ml    = models.IntegerField(default=450)
    blood_group  = models.CharField(max_length=3)
    hiv_test     = models.CharField(max_length=4, choices=TEST_RESULT, default='pass')
    hep_b_test   = models.CharField(max_length=4, choices=TEST_RESULT, default='pass')
    hep_c_test   = models.CharField(max_length=4, choices=TEST_RESULT, default='pass')
    malaria_test = models.CharField(max_length=4, choices=TEST_RESULT, default='pass')
    syphilis_test= models.CharField(max_length=4, choices=TEST_RESULT, default='pass')
    status       = models.CharField(max_length=10, choices=STATUS, default='accepted')
    recorded_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.full_name} - {self.donation_date}"

    def all_tests_passed(self):
        return all([
            self.hiv_test == 'pass',
            self.hep_b_test == 'pass',
            self.hep_c_test == 'pass',
            self.malaria_test == 'pass',
            self.syphilis_test == 'pass',
        ])
