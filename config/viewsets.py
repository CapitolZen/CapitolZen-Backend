from mcs.users.filters import ResourceOwnerFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets
from rest_framework import mixins


class GenericBaseViewSet(viewsets.GenericViewSet):
    """

    """
    lookup_field = 'pk'
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
    )
    ordering = ('-created', )

    def get_serializer(self, *args, **kwargs):
        """
        Customize get serializer to enable adding context to the context
        that is passed to the serializer to enable what the docs suggest
        you are able to do but is not currently possible on ModelViewSets
        http://bit.ly/including-extra-context
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = {
            **self.get_serializer_context(),
            **kwargs.get('context', {})
        }
        return serializer_class(*args, **kwargs)


class BasicViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericBaseViewSet):
    pass


class GenericOwnerBasedViewSet(GenericBaseViewSet):
    """
    Make no assumptions regarding what the endpoint wants to do.
    Usage:
    class MyAwesomeEndpoint(mixins.CreateModelMixin, GenericOwnerBasedViewSet)
    """
    permission_classes = (DRYPermissions, )
    filter_backends = GenericBaseViewSet.filter_backends\
        + (ResourceOwnerFilterBackend,)


class OwnerBasedViewSet(BasicViewSet):
    permission_classes = (DRYPermissions, )
    filter_backends = BasicViewSet.filter_backends\
        + (ResourceOwnerFilterBackend,)
