import uuid

import pytest

from modules.task_queue.tasks import log_results
from utils.custom_dataclasses import ResultEvent

pytestmark = pytest.mark.parametrize(
    "test_target, test_module, test_result",
    [("target_1", "module_1", "result_1"), ("target_2", "module_2", "result_2")],
)


class TestLogResults:
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
