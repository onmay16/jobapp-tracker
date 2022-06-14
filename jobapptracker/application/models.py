from django.db import models

from accounts.models import User

class Status(models.Model):
    name = models.CharField(max_length=30)
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=255)
    company_email = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Application(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    position = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date_created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, null=True)
    job_post = models.URLField(null=True)
    note = models.TextField(null=True, blank=True)
    company_mail = models.EmailField(null=True, blank=True)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, null=True)