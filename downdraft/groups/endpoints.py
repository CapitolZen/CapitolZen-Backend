from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from downdraft.proposals.models import Bill, Wrapper


from .serializers import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        return GroupSerializer

    @detail_route(methods=['post'])
    def add_bill(self, request):
        group = self.get_object()
        bill = Bill.objects.get(state=request.data['state'], state_id=request.data['state_id'])
        w = Wrapper(
            organization=request.user.organization,
            bill=bill
        )
        w.update_group(group.id, request.position)
        w.save()
        Response({"status_code": status.HTTP_200_OK, "detail": "Bill added", "wrapper": w})
