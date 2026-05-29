from django.core.exceptions import ValidationError
from .repositories import (
    PipelineRepository,
    PipelineStageRepository,
    DealRepository
)
from .models import PipelineStage


class PipelineService:

    @staticmethod
    def create(data, user):
        data["created_by"] = user
        return PipelineRepository.create(**data)

    @staticmethod
    def delete(pipeline):
        if pipeline.stages.filter(deals__isnull=False).exists():
            raise ValidationError("Cannot delete pipeline with existing deals.")
        pipeline.delete()


class PipelineStageService:

    @staticmethod
    def create(data):
        return PipelineStageRepository.create(**data)

    @staticmethod
    def reorder(pipeline, stage_orders):
        stages = {str(s.id): s for s in pipeline.stages.all()}

        for item in stage_orders:
            stage = stages.get(str(item["id"]))
            if stage:
                stage.order = item["order"]
                stage.save()

        return pipeline.stages.all()


class DealService:

    @staticmethod
    def create(data, user):
        data["created_by"] = user
        data["owner"] = user
        return DealRepository.create(**data)

    @staticmethod
    def move_stage(deal, new_stage_id):
        new_stage = PipelineStage.objects.get(id=new_stage_id)

        if deal.pipeline_stage.pipeline != new_stage.pipeline:
            raise ValidationError("Cannot move deal across pipelines.")

        deal.pipeline_stage = new_stage
        deal.save()
        return deal