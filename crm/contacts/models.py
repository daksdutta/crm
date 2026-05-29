from django.db import models
from core.models import BaseModel
from companies.models import Company
from accounts.models import User,Organization


class Contact(BaseModel):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name="contacts")
    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="contacts",db_index=True)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name="contacts",db_index=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"