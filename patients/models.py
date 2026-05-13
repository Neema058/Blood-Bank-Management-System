from django.db import models

BLOOD_GROUPS = (
    ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
    ('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-'),
)

class Patient(models.Model):
    GENDER = (('M','Male'),('F','Female'),('O','Other'))

    full_name    = models.CharField(max_length=100)
    age          = models.IntegerField()
    gender       = models.CharField(max_length=1, choices=GENDER)
    blood_group  = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    hospital_name= models.CharField(max_length=150)
    doctor_name  = models.CharField(max_length=100, blank=True)
    contact      = models.CharField(max_length=15)
    address      = models.TextField(blank=True)
    registered_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.blood_group}) - {self.hospital_name}"

    @property
    def total_requests(self):
        return self.bloodrequest_set.count()
