import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField
from model_utils.models import TimeStampedModel


class AbstractBaseModel(TimeStampedModel):
    """
    An abstract model class used for all models.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metadata = JSONField(blank=True, null=True)

    class Meta:
        abstract = True
