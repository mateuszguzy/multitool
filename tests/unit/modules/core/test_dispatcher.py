import pytest

from modules.core.dispatcher.dispatcher import Dispatcher
from tests.conftest import TEST_TARGET, DISPATCHER_MODULE_PATH


class TestDispatcher:
    test_target = TEST_TARGET
    module_path = DISPATCHER_MODULE_PATH

    @pytest.mark.parametrize(
        "event",
        [pytest.lazy_fixture("start_directory_bruteforce_module_event_fixture")],  # type: ignore
    )
    def test_run_start_module_event_success(
        self,
        event,
        mock_dispatcher_parse_workflow_yaml_function,
        mock_dispatcher_interpret_start_module_event_function,
        mock_dispatcher_interpret_result_event_function,
    ):
        dispatcher = Dispatcher(event)
        dispatcher.run()

        # assertions
        dispatcher._interpret_start_module_event.assert_called_once()
        assert dispatcher._interpret_result_event.call_count == 0

    @pytest.mark.parametrize(
        "event",
        [pytest.lazy_fixture("directory_bruteforce_result_event_fixture")],  # type: ignore
    )
    def test_run_result_event_success(
        self,
        event,
        mock_dispatcher_parse_workflow_yaml_function,
        mock_dispatcher_interpret_start_module_event_function,
        mock_dispatcher_interpret_result_event_function,
    ):
        dispatcher = Dispatcher(event)
        dispatcher.run()

        # assertions
        assert dispatcher._interpret_start_module_event.call_count == 0
        dispatcher._interpret_result_event.assert_called_once()

    @pytest.mark.parametrize(
        "event, mapper_mock, task",
        [
            (
                pytest.lazy_fixture("start_directory_bruteforce_module_event_fixture"),  # type: ignore
                pytest.lazy_fixture("mock_dispatcher_module_mapper_with_directory_bruteforce_task"),  # type: ignore
                pytest.lazy_fixture("mock_dispatcher_directory_bruteforce_task"),  # type: ignore
            ),
            (
                pytest.lazy_fixture("start_email_scraper_module_event_fixture"),  # type: ignore
                pytest.lazy_fixture("mock_dispatcher_module_mapper_with_email_scraper_task"),  # type: ignore
                pytest.lazy_fixture("mock_dispatcher_email_scraper_task"),  # type: ignore
            ),
            (
                pytest.lazy_fixture("start_port_scan_module_event_fixture"),  # type: ignore
                pytest.lazy_fixture("mock_dispatcher_module_mapper_with_port_scan_task"),  # type: ignore
                pytest.lazy_fixture("mock_dispatcher_port_scan_task"),  # type: ignore
            ),
        ],
    )
    def test_interpret_start_module_event_success(
        self,
        event,
        mapper_mock,
        task,
        mock_dispatcher_workflow,
    ):
        dispatcher = Dispatcher(event=event)
        dispatcher._interpret_start_module_event(event=event)

        # assertions
        task.assert_called_once_with(event=event)

    @pytest.mark.parametrize(
        "event, mapper_mock, task",
        [
            (
                pytest.lazy_fixture("directory_bruteforce_result_event_fixture"),  # type: ignore
                pytest.lazy_fixture("mock_dispatcher_module_mapper_with_email_scraper_task"),  # type: ignore
                pytest.lazy_fixture("mock_dispatcher_email_scraper_task"),  # type: ignore
            ),
        ],
    )
    def test_interpret_result_event_success(
        self,
        event,
        mapper_mock,
        task,
        mock_dispatcher_workflow,
    ):
        dispatcher = Dispatcher(event=event)
        dispatcher._interpret_result_event(event=event)

        # assertions
        task.assert_called_once_with(event=event)

    @pytest.mark.parametrize(
        "event",
        [
            pytest.lazy_fixture("email_scraper_result_event_fixture"),  # type: ignore
            pytest.lazy_fixture("port_scan_result_event_fixture"),  # type: ignore
        ],
    )
    def test_interpret_result_event_without_passing_result(
        self,
        event,
        mock_dispatcher_directory_bruteforce_task,
        mock_dispatcher_email_scraper_task,
        mock_dispatcher_port_scan_task,
    ):
        """
        Test modules that do not pass their results to other modules.
        """

        dispatcher = Dispatcher(event=event)
        dispatcher._interpret_result_event(event=event)

        # assertions
        assert mock_dispatcher_directory_bruteforce_task.call_count == 0
        assert mock_dispatcher_email_scraper_task.call_count == 0
        assert mock_dispatcher_port_scan_task.call_count == 0

    def test_parse_workflow_yaml_success(
        self,
        mocker,
    ):
        dispatcher = Dispatcher(event=mocker.Mock())
        dispatcher._parse_workflow_yaml()

        # assertions
        assert isinstance(dispatcher.workflow, dict)
        assert list(dispatcher.workflow.keys()) == ["version", "modules"]
