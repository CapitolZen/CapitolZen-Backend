from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


class AbstractNoIDModel(models.Model):
    """

    """
    created = models.DateTimeField(default=timezone.now, db_index=True)
    modified = models.DateTimeField(db_index=True, default=timezone.now)
    metadata = JSONField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not kwargs.pop('skip_modified', False):
            self.modified = timezone.now()
        super(AbstractNoIDModel, self).save(*args, **kwargs)


class AbstractBaseModel(AbstractNoIDModel):
    """
    An abstract model class used for all models.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True

    @property
    def doc_type(self):
        return self.__class__.__name__.lower()
