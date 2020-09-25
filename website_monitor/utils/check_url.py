import logging
import time

import requests

from api.models import CheckTaskResult

logger = logging.getLogger(__name__)


def check_url(check_task):
    try:
        start_time = time.time()
        response = requests.get(check_task.url)
        stop_time = time.time()
    except requests.exceptions.ConnectionError:
        logger.exception(f'Connection error.')
        return
    except requests.exceptions.Timeout:
        logger.exception(f'Timeout error.')
        return

    response_time = stop_time - start_time
    if response.status_code == requests.codes.ok:
        result_status = CheckTaskResult.UP
    elif response.status_code >= requests.codes.bad:
        result_status = CheckTaskResult.DOWN

    check_task_result = CheckTaskResult(
        check_task=check_task,
        status=result_status,
        status_code=response.status_code,
        response_time=response_time,
    )
    try:
        check_task_result.save()
        logger.debug(f'Created Result for {check_task}')
    except ValueError:
        logger.exception(f'Failed to create result for {check_task}.')

    try:
        check_task.last_response_status = result_status
        check_task.save()
        logger.debug(f'Updated last response status for {check_task}')
    except ValueError:
        logger.exception(f'Failed to update response status for {check_task}.')
