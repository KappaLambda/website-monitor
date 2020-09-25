from django.contrib import admin

from api.models import CheckTask, CheckTaskJob, CheckTaskResult, UserProfile


class CheckTaskAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'id',
        'url',
        'interval',
        'owner',
        'date_created',
        'is_deleted',
        'last_response_status',
    )

    readonly_fields = (
        'date_created',
        'uuid',
        'is_deleted',
    )

    def get_queryset(self, request):
        qs = self.model.objects_unfiltered.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class CheckTaskResultAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'check_task_url',
        'status',
        'status_code',
        'check_task',
        'owner',
    )

    readonly_fields = (
        'check_task',
        'status',
        'status_code',
        'response_time',
        'date_received',
        'response_content',
        'owner',
    )

    def check_task_url(self, obj):
        return obj.check_task.url


class CheckTaskJobAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'id',
        'check_task',
        'owner',
        'is_deleted',
        'date_scheduled',
    )

    readonly_fields = (
        'check_task',
        'uuid',
        'is_deleted',
        'date_scheduled',
        'owner',
    )

    def get_queryset(self, request):
        qs = self.model.objects_unfiltered.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'scopes',
    )


admin.site.register(CheckTask, CheckTaskAdmin)
admin.site.register(CheckTaskResult, CheckTaskResultAdmin)
admin.site.register(CheckTaskJob, CheckTaskJobAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
