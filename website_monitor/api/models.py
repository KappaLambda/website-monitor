import uuid

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class CheckTaskExcludeDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class CheckTaskJobExcludeDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class CheckTask(models.Model):
    INTERVAL_CHOICES = (
        (60, '1 min'),
        (120, '2 min'),
        (300, '5 min'),
        (600, '10 min'),
        (1200, '20 min'),
        (1800, '30 min'),
        (3600, '1 hour'),
        (7200, '2 hours'),
        (21600, '6 hours'),
        (43200, '12 hours'),
        (86400, '24 hours'),
    )

    url = models.URLField(
        max_length=200,
    )
    interval = models.PositiveIntegerField(
        choices=INTERVAL_CHOICES,
        default=3600,
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
    )
    date_created = models.DateTimeField(
        auto_now=True,
    )
    is_deleted = models.BooleanField(
        default=False,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    last_response_status = models.CharField(
        max_length=8,
        blank=True,
        null=True,
    )

    objects = CheckTaskExcludeDeletedManager()
    objects_unfiltered = models.Manager()

    def __str__(self):
        return f'CheckTask {self.uuid}'


class CheckTaskResult(models.Model):
    UP = 'UP'
    DOWN = 'DOWN'
    DEGRADED = 'DEGRADED'

    STATUS_CHOICES = (
        (UP, 'Up'),
        (DOWN, 'Down'),
        (DEGRADED, 'Degraded'),
    )

    check_task = models.ForeignKey(
        CheckTask,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=8,
        choices=STATUS_CHOICES,
    )
    status_code = models.PositiveSmallIntegerField(
    )
    response_time = models.FloatField(
        validators=[MinValueValidator(0)],
    )
    date_received = models.DateTimeField(
        auto_now=True,
    )
    response_content = models.TextField(
        blank=True,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'CheckTaskResult {self.id}'

    def save(self, **kwargs):
        self.owner = self.check_task.owner
        super(CheckTaskResult, self).save()


class CheckTaskJob(models.Model):
    check_task = models.ForeignKey(
        CheckTask,
        on_delete=models.CASCADE,
    )
    uuid = models.CharField(
        max_length=36,
        unique=True,
    )
    is_deleted = models.BooleanField(
        default=False,
    )
    date_scheduled = models.DateTimeField(
        auto_now=True,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    objects = CheckTaskJobExcludeDeletedManager()
    objects_unfiltered = models.Manager()

    def __str__(self):
        return f'CheckTaskJob {self.uuid}'

    def save(self, **kwargs):
        self.owner = self.check_task.owner
        super(CheckTaskJob, self).save()


class UserProfile(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    scopes = models.TextField(blank=True)

    def __str__(self):
        return f'UserProfile {self.user.username}'
