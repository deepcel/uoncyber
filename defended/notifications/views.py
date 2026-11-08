from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(mixins.ListModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """
    GET    /notifications/                 my notifications, newest first; ?unread=true for unread only
    GET    /notifications/unread-count/    {"count": n} for the bell badge
    POST   /notifications/<id>/read/       mark one as read
    POST   /notifications/read-all/        mark all as read
    DELETE /notifications/<id>/            dismiss one
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    # Recent history is enough for a bell menu; older notifications aren't shown.
    LIST_LIMIT = 100

    def get_queryset(self):
        # Users only ever see their own notifications; anyone else's id gives 404.
        return Notification.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        if request.query_params.get('unread') in ('true', '1'):
            qs = qs.filter(is_read=False)

        return Response(self.get_serializer(qs[:self.LIST_LIMIT], many=True).data)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        return Response({'count': self.get_queryset().filter(is_read=False).count()})

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read'])

        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'updated': updated})
