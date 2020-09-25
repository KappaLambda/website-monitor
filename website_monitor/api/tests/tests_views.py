from random import choice
from unittest.mock import patch
from uuid import uuid4

import requests
import requests_mock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import CheckTask, CheckTaskJob, CheckTaskResult
from api.tests.tokens import tokens_dict


class MockJob(object):
    def __init__(self):
        self.id = uuid4()


class BaseTestCase(APITestCase):
    def setUp(self):
        self.data = {
            'url': 'http://example.com',
            'interval': 7200,
        }
        self.check_tasks_url = reverse('check-tasks')

    def _client(self, request_method, data=None, token=None, url=None):
        if token:
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer ' + token,
            )

        if not url:
            url = self.check_tasks_url

        if request_method == 'GET':
            response = self.client.get(url)
        elif request_method == 'POST':
            response = self.client.post(url, data, format='json')
        elif request_method == 'PUT':
            response = self.client.put(url, data, format='json')
        elif request_method == 'DELETE':
            response = self.client.delete(url)
        else:
            raise ValueError('Request method not supported.')

        return response

    @patch('django_rq.get_scheduler')
    def create_check_task(self, data, token, MockScheduler):
        scheduler_mock = MockScheduler()
        scheduler_mock.schedule.return_value = MockJob()
        response = self._client('POST', data, token)
        if response.status_code >= status.HTTP_400_BAD_REQUEST:
            url = None
            check_task_id = None
        else:
            check_task_id = response.json()['id']
            url = reverse('check-task', kwargs={'pk': check_task_id})

        return response, url, check_task_id

    @patch('django_rq.get_scheduler')
    def update_check_task(self, url, token, MockScheduler):
        scheduler_mock = MockScheduler()
        scheduler_mock.schedule.return_value = MockJob()
        scheduler_mock.cancel.return_value = None
        response = self._client('PUT', self.data, token, url)
        return response

    @patch('django_rq.get_scheduler')
    def delete_check_task(self, url, token, MockScheduler):
        scheduler_mock = MockScheduler()
        scheduler_mock.cancel.return_value = None
        response = self._client('DELETE', None, token, url)
        return response


class CheckTaskTestCase(BaseTestCase):
    # Test for successful requests
    def test_get_check_tasks_success(self):
        post_response, _, _ = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        get_response = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_all'],
        )
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            get_response.json(),
            [
                {
                    'id': post_response.json()['id'],
                    'url': post_response.json()['url'],
                    'interval': post_response.json()['interval'],
                    'uuid': post_response.json()['uuid'],
                    'date_created': post_response.json()['date_created'],
                    'is_deleted': post_response.json()['is_deleted'],
                    'owner': post_response.json()['owner'],
                    'last_response_status': post_response.json()['last_response_status'],  # noqa: E501
                },
            ],
        )

    def test_get_check_tasks_no_tasks_exist_success(self):
        response = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_all'],
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_create_check_task_success(self):
        response, _, _ = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.data.items() <= response.data.items())

    def test_get_single_check_task_success(self):
        post_response, url, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        get_response = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_all'],
            url=url,
        )
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            post_response.data.items() <= get_response.data.items(),
        )

    def test_update_single_check_task_success(self):
        post_response, url, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        put_response = self.update_check_task(
            url,
            tokens_dict['test_user_01_scopes_all'],
        )
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            post_response.data.items() != put_response.data.items(),
        )

    def test_delete_check_task_success(self):
        post_response, url, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        del_response = self.delete_check_task(
            url,
            tokens_dict['test_user_01_scopes_all'],
        )
        check_task = CheckTask.objects_unfiltered.get(pk=check_task_id)
        self.assertEqual(del_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(check_task.is_deleted)

    # Test for bad requests
    def test_create_check_task_with_bad_data_fails(self):
        bad_data = [
            {'interval': 3600},  # 'url' key,value pair missing
            {'xxx': 'http://example.com'},  # wrong key name
            {'url': 'XXXXXX'},  # 'url' value is not a valid url
            {
                'url': 'http://example.com',
                'interval': 360,  # Invalid interval value
            },
        ]
        for data in bad_data:
            response, _, _ = self.create_check_task(
                data,
                tokens_dict['test_user_01_scopes_all'],
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )

    def test_get_check_task_not_exist(self):
        url = reverse('check-task', kwargs={'pk': 1})
        response = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_all'],
            url=url,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CheckTaskJobTestCase(BaseTestCase):
    # Test for successful requests
    def test_create_check_task_job_success(self):
        _, _, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        self.assertTrue(
            CheckTaskJob.objects.filter(
                check_task=check_task_id,
            ).exists(),
        )

    def test_update_single_check_task_job_success(self):
        _, url, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        job = CheckTaskJob.objects.get(check_task=check_task_id)
        self.update_check_task(
            url,
            tokens_dict['test_user_01_scopes_all'],
        )
        new_job = CheckTaskJob.objects.get(check_task=check_task_id)
        self.assertEqual(job.check_task.uuid, new_job.check_task.uuid)
        self.assertNotEqual(job.uuid, new_job.uuid)
        self.assertLess(job.date_scheduled, new_job.date_scheduled)

    def test_delete_check_task_job_success(self):
        _, url, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        self.delete_check_task(
            url,
            tokens_dict['test_user_01_scopes_all'],
        )
        job = CheckTaskJob.objects_unfiltered.get(check_task=check_task_id)
        self.assertTrue(job.is_deleted)


class CheckTaskResultTestCase(BaseTestCase):
    def check_task_result_factory(self, check_task, desired_num_of_results=1):
        status_codes_farm = [200, 400, 401, 403, 404, 500]
        responses = []
        results = []
        for i in range(desired_num_of_results):
            status_code = choice(status_codes_farm)
            with requests_mock.Mocker() as mocked_request:
                mocked_request.get(check_task.url, status_code=status_code)
                response = requests.get(check_task.url)
                responses.append(response)
            if response.status_code == requests.codes.ok:
                result_status = CheckTaskResult.UP
            elif response.status_code >= requests.codes.bad:
                result_status = CheckTaskResult.DOWN
            try:
                result = CheckTaskResult.objects.create(
                    check_task=check_task,
                    status=result_status,
                    status_code=response.status_code,
                    response_time=0.5,
                )
                result.save()
                results.append(result)
            except ValueError:
                raise

        return responses, results

    def test_create_check_task_result_success(self):
        _, _, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        check_task = CheckTask.objects.get(id=check_task_id)
        responses, results = self.check_task_result_factory(check_task, 10)
        for i in range(len(responses)):
            self.assertEqual(responses[i].status_code, results[i].status_code)
            self.assertEqual(results[i].owner, check_task.owner)

    def test_get_results_for_check_task_no_results_success(self):
        _, _, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        url = reverse('check-task-results', kwargs={'pk': check_task_id})
        response = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_all'],
            url=url,
        )
        next_endpoint = response.data['next']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(next_endpoint, None)
        self.assertEqual(len(response.data['results']), 0)

    def test_get_all_check_task_results_only_ten_or_less_success(self):
        _, _, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        check_task = CheckTask.objects.get(id=check_task_id)
        url = reverse('check-task-results', kwargs={'pk': check_task_id})
        amount_of_results = 10
        self.check_task_result_factory(check_task, amount_of_results)
        response = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_all'],
            url=url,
        )
        next_endpoint = response.data['next']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], amount_of_results)
        self.assertEqual(next_endpoint, None)
        self.assertEqual(len(response.data['results']), 10)
        for i in range(len(response.data)):
            self.assertEqual(
                response.data['results'][i]['owner'],
                check_task.owner.pk,
            )

    def test_get_all_check_task_results_more_than_ten_success(self):
        _, _, check_task_id = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        check_task = CheckTask.objects.get(id=check_task_id)
        amount_of_results = 50
        self.check_task_result_factory(check_task, amount_of_results)
        url = reverse('check-task-results', kwargs={'pk': check_task_id})

        if amount_of_results % 10 == 0:
            number_of_pages = amount_of_results//10
        else:
            number_of_pages = amount_of_results//10 + 1

        for page in range(number_of_pages):
            response = self._client(
                'GET',
                token=tokens_dict['test_user_01_scopes_all'],
                url=f'{url}?page={page+1}',
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['count'], amount_of_results)
            if page+1 < number_of_pages:
                next_endpoint = response.data['next'].split('http://testserver')[1]  # noqa: E501
                self.assertEqual(next_endpoint, f'{url}?page={page+2}')
                self.assertEqual(len(response.data['results']), 10)
                for i in range(len(response.data)):
                    self.assertEqual(
                        response.data['results'][i]['owner'],
                        check_task.owner.pk,
                    )
            else:
                next_endpoint = response.data['next']
                self.assertEqual(next_endpoint, None)
                for i in range(len(response.data)):
                    self.assertEqual(
                        response.data['results'][i]['owner'],
                        check_task.owner.pk,
                    )
                if amount_of_results % 10 != 0:
                    self.assertEqual(
                        len(response.data['results']),
                        amount_of_results % 10,
                    )
                else:
                    self.assertEqual(len(response.data['results']), 10)


class PermissionsTestCase(BaseTestCase):
    def test_create_check_task_not_authenticated(self):
        response, _, _ = self.create_check_task(self.data, None)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_check_tasks_not_authenticated(self):
        response = self._client('GET')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_single_check_task_not_authenticated(self):
        url = reverse('check-task', kwargs={'pk': 1})
        response = self._client('GET', url=url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_single_check_task_result_not_authenticated(self):
        url = reverse('check-task-results', kwargs={'pk': 1})
        response = self._client('GET', url=url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_check_tasks_user_gets_only_tasks_owned(self):
        # Create check task for test_user_01
        _, _, check_task_id_user_01 = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        check_task_user_01 = CheckTask.objects.get(pk=check_task_id_user_01)

        # Create check task for test_user_02
        _, _, check_task_id_user_02 = self.create_check_task(
            self.data,
            tokens_dict['test_user_02_scopes_all'],
        )
        check_task_user_02 = CheckTask.objects.get(pk=check_task_id_user_02)

        response_user_01 = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_all'],
        )
        response_user_02 = self._client(
            'GET',
            token=tokens_dict['test_user_02_scopes_all'],
        )
        self.assertEqual(response_user_01.status_code, status.HTTP_200_OK)
        self.assertEqual(response_user_02.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response_user_01.data) == 1)
        self.assertTrue(len(response_user_02.data) == 1)
        self.assertEqual(
            response_user_01.data[0]['owner'],
            check_task_user_01.owner.pk,
        )
        self.assertEqual(
            response_user_02.data[0]['owner'],
            check_task_user_02.owner.pk,
        )

    def test_get_check_task_of_another_user(self):
        _, url_user_01, _ = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        _, url_user_02, _ = self.create_check_task(
            self.data,
            tokens_dict['test_user_02_scopes_all'],
        )
        response_user_01 = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_all'],
            url=url_user_02,
        )
        response_user_02 = self._client(
            'GET',
            token=tokens_dict['test_user_02_scopes_all'],
            url=url_user_01,
        )
        self.assertEqual(
            response_user_01.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            response_user_02.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_get_all_results_for_check_task_of_another_user(self):
        check_task_ids = []
        # Create a check task and a result for test_user_01
        _, _, check_task_id_user_01 = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        check_task_ids.append(check_task_id_user_01)
        url_user_01 = reverse(
            'check-task-results',
            kwargs={'pk': check_task_id_user_01},
        )
        # Create a check task and a result for test_user_02
        _, _, check_task_id_user_02 = self.create_check_task(
            self.data,
            tokens_dict['test_user_02_scopes_all'],
        )
        check_task_ids.append(check_task_id_user_02)
        url_user_02 = reverse(
            'check-task-results',
            kwargs={'pk': check_task_id_user_02},
        )

        for id in check_task_ids:
            check_task = CheckTask.objects.get(id=id)
            CheckTaskResult.objects.create(
                check_task=check_task,
                status=CheckTaskResult.UP,
                status_code=200,
                response_time=0.5,
            )

        # test_user requests results for task of test_user_b and vice versa
        response_user_01 = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_all'],
            url=url_user_02,
        )
        response_user_02 = self._client(
            'GET',
            token=tokens_dict['test_user_02_scopes_all'],
            url=url_user_01,
        )
        self.assertEqual(
            response_user_01.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            response_user_02.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_get_check_tasks_token_has_no_scope(self):
        self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        response = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_none'],
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_check_tasks_token_has_no_scope(self):
        response, _, _ = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_none'],
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_check_tasks_token_has_only_read_scope(self):
        self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        response = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_read'],
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_check_tasks_token_has_only_read_scope(self):
        response, _, _ = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_read'],
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_check_tasks_token_has_only_write_scope(self):
        self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_all'],
        )
        response = self._client(
            'GET',
            token=tokens_dict['test_user_01_scopes_write'],
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_check_tasks_token_has_only_write_scope(self):
        response, _, _ = self.create_check_task(
            self.data,
            tokens_dict['test_user_01_scopes_write'],
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
