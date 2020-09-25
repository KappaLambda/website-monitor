import logging

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import CheckTask, CheckTaskResult
from api.serializers import CheckTaskResultSerializer, CheckTaskSerializer
from utils import scheduler

logger = logging.getLogger(__name__)


class HomeView(APIView):
    required_scopes = []
    permission_classes = []
    pagination_class = None

    def get(self, request):
        return Response({'message': 'API HOME PAGE'})


class CheckTaskList(generics.ListCreateAPIView):
    required_scopes = ['read:check-tasks', 'write:check-tasks']
    serializer_class = CheckTaskSerializer
    pagination_class = None

    def get_queryset(self):
        return CheckTask.objects.filter(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        data = request.data
        data['owner'] = request.user.pk
        serializer = CheckTaskSerializer(data=data)
        if serializer.is_valid():
            check_task = serializer.save()
            logger.debug(f'Created {check_task}.')
            scheduler.schedule(check_task)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        logger.error(f'CheckTask Serializer error: {serializer.errors}.')
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class CheckTaskDetails(generics.RetrieveUpdateDestroyAPIView):
    required_scopes = ['read:check-tasks', 'write:check-tasks']
    queryset = CheckTask.objects.all()
    serializer_class = CheckTaskSerializer
    pagination_class = None

    def update(self, request, *args, **kwargs):
        check_task = self.get_object()
        serializer = self.get_serializer(
            check_task,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            self.perform_update(serializer)
            logger.debug(f'Updated {check_task}.')
            scheduler.unschedule(check_task)
            scheduler.schedule(check_task)
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.error(f'CheckTask Serializer error: {serializer.errors}.')
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        check_task = self.get_object()
        scheduler.unschedule(check_task)
        serializer = self.get_serializer(
            check_task,
            data={'is_deleted': True},
            partial=True,
        )
        if serializer.is_valid():
            check_task = serializer.save()
            logger.debug(f'Deleted {check_task}')
            return Response(status=status.HTTP_204_NO_CONTENT)


class CheckTaskResultList(generics.ListAPIView):
    required_scopes = ['read:check-tasks', 'write:check-tasks']
    serializer_class = CheckTaskResultSerializer

    def get_queryset(self):
        checktask_qs = CheckTask.objects.filter(
            pk=self.kwargs['pk'],
            owner=self.request.user,
        )
        if checktask_qs.exists():
            return (
                CheckTaskResult.objects.
                filter(check_task=self.kwargs['pk'])
                .order_by('-id')
            )

        raise PermissionDenied
