import uuid
from unittest import mock

import pytest

from config.settings import PUBSUB_RESULTS_CHANNEL_NAME, STEERING_MODULE
from modules.task_queue.tasks import (
    log_results,
    pass_result_event,
    start_module_event,
    live_results_listener_task,
)
from utils.custom_dataclasses import ResultEvent

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
            mock.call(f"START::{mock_encoded_event.id}::{self.task_name}::{mock_encoded_event.destination_module}")
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
