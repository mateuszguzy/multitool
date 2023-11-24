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
    socket_request,
    email_scraper_web_request,
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

        with pytest.raises(Exception):
            log_results(event)


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
            text=None,
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
            text=None,
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


class TestSocketRequest:
    request_method = "get"
    target = "test_target"
    port = 80
    module = "port_scan"

    def test_socket_request(self, mocker, mock_pass_result_event):
        mocker.patch(
            "modules.task_queue.tasks.SocketManager.run",
            return_value=0,  # response indicating successful connection
        )

        result = socket_request(target=self.target, port=self.port, module=self.module)

        assert result == self.port

    def test_socket_fail(self, mocker, mock_pass_result_event):
        mocker.patch(
            "modules.task_queue.tasks.SocketManager.run",
            return_value=1,  # response indicating failed connection
        )

        result = socket_request(target=self.target, port=self.port, module=self.module)

        assert result is None


class TestEmailScraperWebRequest:
    test_target = "http://example.com"
    test_response_text = "Response Text"

    @pytest.mark.parametrize(
        "test_response_status, test_response_text",
        [(True, test_response_text), (False, None)],
    )
    def test_email_scraper_web_success(
        self, mocker, test_response_status, test_response_text
    ):
        mocked_response = mocker.Mock(
            ok=test_response_status, text=self.test_response_text
        )
        mocker.patch(
            f"{TASK_QUEUE_MODULE_PATH}.requests.get",
            return_value=mocked_response,
        )

        result = email_scraper_web_request(target=self.test_target)

        assert result == test_response_text

    def test_email_scraper_web_fail(self, mocker):
        mocker.patch(
            f"{TASK_QUEUE_MODULE_PATH}.requests.get",
            side_effect=Exception,
        )

        with pytest.raises(Exception):
            email_scraper_web_request(target=self.test_target)
