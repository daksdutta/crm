from django.db import models
from core.models import BaseModel
from django.conf import settings
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL

class Pipeline(BaseModel):
    organization = models.ForeignKey("accounts.Organization",on_delete=models.CASCADE,related_name="pipelines")
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="created_pipelines")

    class Meta:
        unique_together = ("organization", "name")
        indexes = [
            models.Index(fields=["organization"]),
        ]
    
    def clean(self):
        if self.is_default:
            qs = Pipeline.objects.filter(organization=self.organization,is_default=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError("Only one default pipeline allowed per organization.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.organization})"
    
class PipelineStage(BaseModel):
    pipeline = models.ForeignKey(Pipeline,on_delete=models.CASCADE,related_name="stages")
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField()
    is_closed_stage = models.BooleanField(default=False)
    is_won_stage = models.BooleanField(default=False)

    def clean(self):
        if self.is_won_stage:
            qs = PipelineStage.objects.filter(pipeline=self.pipeline,is_won_stage=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError("Only one WON stage allowed per pipeline.")

        if self.is_won_stage and not self.is_closed_stage:
            raise ValidationError("A WON stage must also be a CLOSED stage.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.pipeline.name})"

    class Meta:
        unique_together = ("pipeline", "order")
        ordering = ["order"]
        indexes = [models.Index(fields=["pipeline", "order"]),]

    def __str__(self):
        return f"{self.name} ({self.pipeline.name})"
    
class Deal(BaseModel):

    STATUS_CHOICES = (
        ("OPEN", "Open"),
        ("WON", "Won"),
        ("LOST", "Lost"),
    )

    organization = models.ForeignKey("accounts.Organization",on_delete=models.CASCADE,related_name="deals")
    name = models.CharField(max_length=255)
    company = models.ForeignKey("companies.Company",on_delete=models.SET_NULL,null=True,blank=True,related_name="deals")
    contact = models.ForeignKey("contacts.Contact",on_delete=models.SET_NULL,null=True,blank=True,related_name="deals")
    pipeline_stage = models.ForeignKey(PipelineStage,on_delete=models.PROTECT,related_name="deals")
    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="owned_deals")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expected_close_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default="OPEN")
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="created_deals")

    class Meta:
        indexes = [
            models.Index(fields=["organization"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["pipeline_stage"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def clean(self):
        # Ensure stage belongs to same organization
        if self.pipeline_stage.pipeline.organization != self.organization:
            raise ValidationError("Pipeline stage must belong to the same organization.")

    def save(self, *args, **kwargs):
        # Auto update status based on stage
        if self.pipeline_stage.is_closed_stage:
            if self.pipeline_stage.is_won_stage:
                self.status = "WON"
            else:
                self.status = "LOST"
        else:
            self.status = "OPEN"

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name