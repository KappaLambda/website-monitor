from rest_framework import serializers

from api.models import CheckTask, CheckTaskJob, CheckTaskResult


class CheckTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckTask
        fields = (
            'id',
            'url',
            'interval',
            'uuid',
            'date_created',
            'is_deleted',
            'owner',
            'last_response_status',
        )


class CheckTaskResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckTaskResult
        fields = (
            'id',
            'check_task',
            'status',
            'status_code',
            'response_time',
            'date_received',
            'response_content',
            'owner',
        )


class CheckTaskJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckTaskJob
        fields = (
            'id',
            'check_task',
            'uuid',
            'is_deleted',
            'date_scheduled',
            'owner',
        )
