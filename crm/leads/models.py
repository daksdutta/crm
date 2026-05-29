from django.db import models
from core.models import BaseModel
from contacts.models import Contact
from accounts.models import User,Organization


class Lead(BaseModel):

    LEAD_STATUS = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("qualified", "Qualified"),
        ("lost", "Lost"),
        ("converted", "Converted"),
    ]

    title = models.CharField(max_length=255)
    contact = models.ForeignKey(Contact,on_delete=models.CASCADE,related_name="leads")
    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="leads",db_index=True)
    status = models.CharField(max_length=20,choices=LEAD_STATUS,default="new")
    source = models.CharField(max_length=100,blank=True)
    notes = models.TextField(blank=True)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name="leads",db_index=True)

    def __str__(self):
        return self.title