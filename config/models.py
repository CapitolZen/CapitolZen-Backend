from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from thorn import ModelEvent


class AbstractNoIDModel(models.Model):
    # We do not use auto_now_add or auto_now because they cannot be overwritten
    # in tests and some core devs have a thread open to eliminate them
    # https://code.djangoproject.com/ticket/22995
    created = models.DateTimeField(default=timezone.now, db_index=True)
    modified = models.DateTimeField(db_index=True, default=timezone.now)
    metadata = JSONField(blank=True, null=True)

    class Meta:
        abstract = True


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

    def save(self, *args, **kwargs):
        if not kwargs.pop('skip_modified', False):
            self.modified = timezone.now()
        super(AbstractBaseModel, self).save(*args, **kwargs)


class ListenToModelEvent(ModelEvent):
    def get_absolute_url(self, instance):
        try:
            return instance.get_absolute_url()
        except AttributeError:
            return None
