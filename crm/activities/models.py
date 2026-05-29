from django.db import models
from core.models import BaseModel
from accounts.models import User, Organization
from leads.models import Lead
from contacts.models import Contact


class ActivityType(BaseModel):

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Activity(BaseModel):

    ACTIVITY_STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    ]

    title = models.CharField(max_length=255)
    activity_type = models.ForeignKey(ActivityType, on_delete=models.SET_NULL, null=True, related_name="activities")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities", db_index=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True, related_name="activities")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True, related_name="activities")
    deal = models.ForeignKey("deals.Deal", on_delete=models.CASCADE, null=True, blank=True, related_name="activities")
    notes = models.TextField(blank=True)
    activity_date = models.DateTimeField()
    next_followup_date = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    meeting_link = models.URLField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="activities", db_index=True)
    status = models.CharField(
        max_length=20,
        choices=ACTIVITY_STATUS_CHOICES,
        default="scheduled"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=["owner", "activity_date"]),
            models.Index(fields=["lead", "activity_date"]),
            models.Index(fields=["contact", "activity_date"]),
            models.Index(fields=["deal", "activity_date"]),
            models.Index(fields=["organization", "activity_date"]),
        ]
        ordering = ["-activity_date"]
    
    def __str__(self):
        return self.title