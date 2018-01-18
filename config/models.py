from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from django.forms.models import model_to_dict


class ModelDiffMixin(object):
    """
    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.
    """

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])


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
