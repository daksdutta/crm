from django.db import models
from core.models import BaseModel
from accounts.models import User,Organization


class Company(BaseModel):

    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="companies",db_index=True)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name="companies",db_index=True)
    
    def __str__(self):
        return self.name