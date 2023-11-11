import uuid
from unittest import mock

import pytest

from config.settings import PUBSUB_RESULTS_CHANNEL_NAME
from modules.task_queue.tasks import log_results, pass_result_event
from utils.custom_dataclasses import ResultEvent


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
            "modules.task_queue.tasks.result_event_encoder", mock_encoded_event
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
            "modules.task_queue.tasks.result_event_encoder", mock_encoded_event
        )

        # assertions
        with pytest.raises(Exception):
            pass_result_event(mock_encoded_event)

        assert mock_task_queue_logger_in_tasks.error.call_count == 1
