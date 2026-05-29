from .models import Pipeline, PipelineStage, Deal


class PipelineRepository:

    @staticmethod
    def create(**kwargs):
        return Pipeline.objects.create(**kwargs)

    @staticmethod
    def get_by_id(pipeline_id):
        return Pipeline.objects.get(id=pipeline_id, is_deleted=False)

    @staticmethod
    def get_by_org(org):
        return Pipeline.objects.filter(organization=org, is_deleted=False)


class PipelineStageRepository:

    @staticmethod
    def create(**kwargs):
        return PipelineStage.objects.create(**kwargs)

    @staticmethod
    def get_by_id(stage_id):
        return PipelineStage.objects.get(id=stage_id, is_deleted=False)

    @staticmethod
    def get_by_pipeline(pipeline):
        return PipelineStage.objects.filter(pipeline=pipeline, is_deleted=False)


class DealRepository:

    @staticmethod
    def create(**kwargs):
        return Deal.objects.create(**kwargs)

    @staticmethod
    def get_by_id(deal_id):
        return Deal.objects.get(id=deal_id, is_deleted=False)

    @staticmethod
    def get_by_org(org):
        return Deal.objects.filter(organization=org, is_deleted=False)