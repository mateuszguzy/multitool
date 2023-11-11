import uuid
from unittest import mock

import pytest

from config.settings import PUBSUB_RESULTS_CHANNEL_NAME, STEERING_MODULE
from modules.task_queue.tasks import (
    log_results,
    pass_result_event,
    start_module_event,
    live_results_listener_task,
    event_listener_task,
    start_event_listeners,
    directory_bruteforce_web_request,
)
from utils.custom_dataclasses import ResultEvent, SessionRequestResponseObject

TASK_QUEUE_MODULE_PATH = "modules.task_queue.tasks"


class TestLogResults:
    @pytest.mark.parametrize(
        "test_target, test_module, test_result",
        [("target_1", "module_1", "result_1"), ("target_2", "module_2", "result_2")],
    )
    def test_log_results_success(
        self, test_target, test_result, test_module, mock_get_logger_function
    ):
        event = ResultEvent(
            id=uuid.uuid4(),
            result=test_result,
            source_module=test_module,
            target=test_target,
        )
        log_results(event)

        # assertions
        mock_get_logger_function.return_value.called_once_with(test_module)
        mock_get_logger_function.return_value.info.assert_called_once_with(
            f"<{test_target}>: {test_result}"
        )

    @pytest.mark.parametrize(
        "test_target, test_module, test_result",
        [("target_1", "module_1", "result_1"), ("target_2", "module_2", "result_2")],
    )
    def test_log_results_fail(
        self,
        test_target,
        test_result,
        test_module,
        mock_get_logger_function_with_exception,
        mock_task_queue_logger_in_tasks,
    ):
        event = ResultEvent(
            id=uuid.uuid4(),
            result=test_result,
            source_module=test_module,
            target=test_target,
        )
        log_results(event)

        # assertions
        mock_get_logger_function_with_exception.return_value.called_once_with(
            test_module
        )
        mock_get_logger_function_with_exception.side_effect = Exception
        mock_task_queue_logger_in_tasks.exception.assert_called_once()


class TestPassResultEvent:
    task_name = "pass_result_event"

    @pytest.mark.parametrize(
        "encoded_event",
        ["encoded_event_1", "encoded_event_2"],
    )
    def test_pass_result_event_success(
        self,
        encoded_event,
        mocker,
        mock_task_queue_logger_in_tasks,
        mock_redis_in_tasks,
    ):
        mock_encoded_event = mocker.Mock(return_value=encoded_event)
        mocker.patch(
            f"{TASK_QUEUE_MODULE_PATH}.result_event_encoder", mock_encoded_event
        )

        pass_result_event(mock_encoded_event)

        # assertions
        mock_redis_in_tasks.publish.assert_called_once_with(
            channel=PUBSUB_RESULTS_CHANNEL_NAME, message=encoded_event
        )
        assert mock_task_queue_logger_in_tasks.debug.call_count == 2
        assert (
            mock.call(f"START::{mock_encoded_event.id}::{self.task_name}")
            in mock_task_queue_logger_in_tasks.debug.call_args_list
        )
        assert (
            mock.call(f"PUBLISHED::{mock_encoded_event.id}")
            in mock_task_queue_logger_in_tasks.debug.call_args_list
        )

    @pytest.mark.parametrize(
        "encoded_event",
        ["encoded_event_1", "encoded_event_2"],
    )
    def test_pass_result_event_fail(
        self,
        encoded_event,
        mocker,
        mock_task_queue_logger_in_tasks,
        mock_redis_in_tasks,
    ):
        mock_encoded_event = mocker.Mock(side_effect=Exception)
        mocker.patch(
            f"{TASK_QUEUE_MODULE_PATH}.result_event_encoder", mock_encoded_event
        )

        # assertions
        with pytest.raises(Exception):
            pass_result_event(mock_encoded_event)

        assert mock_task_queue_logger_in_tasks.error.call_count == 1


class TestStartModuleEvent:
    task_name = "start_module_event"

    @pytest.mark.parametrize(
        "encoded_event",
        ["encoded_event_1", "encoded_event_2"],
    )
    def test_start_module_event_success(
        self,
        encoded_event,
        mocker,
        mock_task_queue_logger_in_tasks,
        mock_redis_in_tasks,
    ):
        mock_encoded_event = mocker.Mock(return_value=encoded_event)
        mocker.patch(
            f"{TASK_QUEUE_MODULE_PATH}.start_module_event_encoder", mock_encoded_event
        )
        start_module_event(mock_encoded_event)

        # assertions
        mock_redis_in_tasks.publish.assert_called_once_with(
            channel=STEERING_MODULE, message=encoded_event
        )
        assert mock_task_queue_logger_in_tasks.debug.call_count == 2
        assert (
            mock.call(
                f"START::{mock_encoded_event.id}::{self.task_name}::{mock_encoded_event.destination_module}"
            )
            in mock_task_queue_logger_in_tasks.debug.call_args_list
        )
        assert (
            mock.call(f"PUBLISHED::{mock_encoded_event.id}")
            in mock_task_queue_logger_in_tasks.debug.call_args_list
        )

    @pytest.mark.parametrize("encoded_event", ["encoded_event_1", "encoded_event_2"])
    def test_start_module_event_fail(
        self,
        encoded_event,
        mocker,
        mock_task_queue_logger_in_tasks,
        mock_redis_in_tasks,
    ):
        mock_encoded_event = mocker.Mock(side_effect=Exception)
        mocker.patch(
            f"{TASK_QUEUE_MODULE_PATH}.start_module_event_encoder", mock_encoded_event
        )

        # assertions
        with pytest.raises(Exception):
            pass_result_event(mock_encoded_event)

        assert mock_task_queue_logger_in_tasks.error.call_count == 1


class TestLiveResultsListenerTask:
    def test_live_results_listener_task_success(
        self,
        mocker,
        mock_task_queue_logger_in_tasks,
        mock_redis_pubsub_subscribe_in_tasks,
        mock_redis_pubsub_listen_in_tasks,
        mock_log_results_task,
    ):
        mocked_event = mocker.Mock()
        mocker.patch(
            f"{TASK_QUEUE_MODULE_PATH}.result_event_data_load",
            return_value=mocked_event,
        )

        live_results_listener_task()

        # assertions
        # pubsub
        mock_redis_pubsub_subscribe_in_tasks.called_once_with(
            PUBSUB_RESULTS_CHANNEL_NAME
        )
        mock_redis_pubsub_listen_in_tasks.assert_called_once()

        # logger
        mock_log_results_task.delay.assert_called_once_with(event=mocked_event)
        assert mock_task_queue_logger_in_tasks.debug.call_count == 2

    def test_live_results_listener_task_fail(
        self,
        mock_redis_pubsub_listen_with_exception_in_tasks,
        mock_redis_pubsub_subscribe_in_tasks,
        mock_task_queue_logger_in_tasks,
    ):
        with pytest.raises(Exception):
            live_results_listener_task()
        mock_task_queue_logger_in_tasks.error.assert_called_once()


class TestEventListenerTask:
    def test_event_listener_task_success(
        self,
        mocker,
        mock_task_queue_logger_in_tasks,
        mock_redis_pubsub_subscribe_in_tasks,
        mock_redis_pubsub_listen_in_tasks,
        mock_dispatcher_in_tasks,
    ):
        mocked_event = mocker.Mock()
        mocker.patch(
            f"{TASK_QUEUE_MODULE_PATH}.start_module_event_data_load",
            return_value=mocked_event,
        )

        event_listener_task(module="test_module")

        # assertions
        mock_dispatcher_in_tasks.assert_called_once()
        # pubsub
        mock_redis_pubsub_subscribe_in_tasks.called_once_with(
            PUBSUB_RESULTS_CHANNEL_NAME
        )
        mock_redis_pubsub_listen_in_tasks.assert_called_once()

        # logger
        assert mock_task_queue_logger_in_tasks.debug.call_count == 2

    def test_event_listener_task_fail(
        self,
        mock_redis_pubsub_listen_with_exception_in_tasks,
        mock_redis_pubsub_subscribe_in_tasks,
        mock_task_queue_logger_in_tasks,
    ):
        with pytest.raises(Exception):
            event_listener_task(module="test_module")
        mock_task_queue_logger_in_tasks.error.assert_called_once()


class TestStartEventListeners:
    @pytest.mark.parametrize(
        "output_after_every_finding",
        [True, False],
    )
    def test_start_event_listener_success(
        self,
        mocker,
        output_after_every_finding,
        mock_event_listener_task,
        mock_live_results_listener_task,
    ):
        mocker_celery_event = mock.Mock()
        mocker.patch(
            f"{TASK_QUEUE_MODULE_PATH}.celery.group",
            return_value=mocker_celery_event,
        )
        start_event_listeners(output_after_every_finding=output_after_every_finding)

        # assertions
        mocker_celery_event.apply_async.assert_called_once()

        if output_after_every_finding:
            mock_live_results_listener_task.delay.assert_called_once()


class TestDirectoryBruteforceWebRequest:
    request_method = "get"
    target = "test_target"
    path = "test_path"
    module = "directory_bruteforce"
    allow_redirects = False
    response_status_code = 200
    response_url = "test_url"

    def test_directory_bruteforce_web_request(self, mocker, mock_pass_result_event):
        mocked_response = SessionRequestResponseObject(
            ok=True,
            status_code=self.response_status_code,
            url=self.response_url,
        )
        mocked_url = mocker.Mock()
        mocker.patch("modules.task_queue.tasks.urlparse", return_value=mocked_url)
        mocker.patch(
            "modules.network.request_manager.request_manager.urlunparse",
            return_value=mocked_url,
        )
        mocker.patch(
            "modules.task_queue.tasks.RequestManager.run", return_value=mocked_response
        )

        result = directory_bruteforce_web_request(
            request_method=self.request_method,
            target=self.target,
            path=self.path,
            module=self.module,
            allow_redirects=self.allow_redirects,
        )

        assert result == mocked_url.path

    def test_directory_bruteforce_web_fail(self, mocker, mock_pass_result_event):
        mocked_response = SessionRequestResponseObject(
            ok=False,
            status_code=self.response_status_code,
            url=self.response_url,
        )
        mocked_url = mocker.Mock()
        mocker.patch("modules.task_queue.tasks.urlparse", return_value=mocked_url)
        mocker.patch(
            "modules.network.request_manager.request_manager.urlunparse",
            return_value=mocked_url,
        )
        mocker.patch(
            "modules.task_queue.tasks.RequestManager.run", return_value=mocked_response
        )

        result = directory_bruteforce_web_request(
            request_method=self.request_method,
            target=self.target,
            path=self.path,
            module=self.module,
            allow_redirects=self.allow_redirects,
        )

        assert result is None
