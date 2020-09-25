import logging
from datetime import datetime

import django_rq

from api.models import CheckTaskJob
from utils.check_url import check_url

logger = logging.getLogger(__name__)


def schedule(check_task):
    scheduler = django_rq.get_scheduler('default', interval=10)
    try:
        job = scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=check_url,
            args=[check_task],
            interval=check_task.interval,
            repeat=None,
        )
        logger.debug(f'Job {job.id} scheduled.')
    except ValueError as ex:
        logger.exception(f'Scheduler exception.')
        return None

    check_task_job = CheckTaskJob(check_task=check_task, uuid=job.id)
    try:
        check_task_job.save()
        logger.debug(f'Created {check_task_job}.')
        return check_task_job
    except ValueError as ex:
        logger.exception(f'Failed to create CheckTaskJob for Job {job.id}.')


def unschedule(check_task):
    scheduler = django_rq.get_scheduler('default', interval=10)
    scheduled_job_list = CheckTaskJob.objects.filter(check_task=check_task)
    for check_task_job in scheduled_job_list:
        scheduler.cancel(check_task_job.uuid)
        logger.debug(f'Job {check_task_job.uuid} unscheduled.')
        check_task_job.is_deleted = True
        try:
            check_task_job.save()
            logger.debug(f'{check_task_job} marked unscheduled.')
        except ValueError as ex:
            logger.exception(f'Failed to mark {check_task_job} unscheduled.')
