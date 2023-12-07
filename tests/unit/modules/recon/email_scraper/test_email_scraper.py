from unittest import mock

import pytest

from tests.conftest import TEST_PATH, TEST_TARGET, EMAIL_SCRAPER_MODULE_PATH


class TestEmailScraper:
    test_target = TEST_TARGET
    test_path = TEST_PATH
    email_scraper_module_path = EMAIL_SCRAPER_MODULE_PATH
    mocked_emails = {"email_1", "email_2"}

    def test_run_tasks_success(
        self, mocker, mock_email_scraper_module, mock_email_scraper_save_results_method
    ):
        mocked_html = mocker.Mock()
        mocker.patch(
            f"{self.email_scraper_module_path}.EmailScraper._get_html",
            return_value=mocked_html,
        )
        mocker.patch(
            f"{self.email_scraper_module_path}.EmailScraper._get_emails",
            return_value=self.mocked_emails,
        )

        mock_email_scraper_module.run()

        assert isinstance(mock_email_scraper_module.url, mock.MagicMock)
        assert mock_email_scraper_module.target == self.test_target
        mock_email_scraper_module._get_html.assert_called_once()
        mock_email_scraper_module._get_emails.assert_called_once_with(html=mocked_html)
        mock_email_scraper_module._save_results.assert_called_once_with(
            results=self.mocked_emails
        )

    def test_run_tasks_fail_1(
        self, mocker, mock_email_scraper_module, mock_email_scraper_save_results_method
    ):
        mocker.patch(
            f"{self.email_scraper_module_path}.EmailScraper._get_html",
            return_value=None,
        )
        mocker.patch(f"{self.email_scraper_module_path}.EmailScraper._get_emails")

        mock_email_scraper_module.run()

        assert isinstance(mock_email_scraper_module.url, mock.MagicMock)
        assert mock_email_scraper_module.target == self.test_target
        mock_email_scraper_module._get_html.assert_called_once()
        assert not mock_email_scraper_module._get_emails.called
        assert not mock_email_scraper_module._save_results.called

    def test_run_tasks_fail_2(
        self, mocker, mock_email_scraper_module, mock_email_scraper_save_results_method
    ):
        mocked_html = mocker.Mock()
        mocker.patch(
            f"{self.email_scraper_module_path}.EmailScraper._get_html",
            return_value=mocked_html,
        )
        mocker.patch(
            f"{self.email_scraper_module_path}.EmailScraper._get_emails",
            return_value=[],
        )

        mock_email_scraper_module.run()

        assert isinstance(mock_email_scraper_module.url, mock.MagicMock)
        assert mock_email_scraper_module.target == self.test_target
        mock_email_scraper_module._get_html.assert_called_once()
        mock_email_scraper_module._get_emails.assert_called_once_with(html=mocked_html)
        assert not mock_email_scraper_module._save_results.called

    def test_get_html_success(
        self, mock_email_scraper_module, mock_email_scraper_web_request_task
    ):
        result = mock_email_scraper_module._get_html()

        mock_email_scraper_web_request_task.delay.assert_called_once()
        assert result == mock_email_scraper_web_request_task.delay().get()

    def test_get_html_fail(
        self,
        mock_email_scraper_module,
        mock_email_scraper_web_request_task_with_exception,
    ):
        with pytest.raises(Exception):
            mock_email_scraper_module._get_html()

    def test_save_results(
        self,
        mocker,
        mock_email_scraper_module,
        mock_pass_results_in_email_scraper_module,
        mock_store_module_results_in_database,
    ):
        mocker.patch(
            f"{self.email_scraper_module_path}.convert_list_or_set_to_dict",
            return_value=self.mocked_emails,
        )
        mocker.patch(
            f"{self.email_scraper_module_path}.ResultEvent",
        )

        mock_email_scraper_module._save_results(results=self.mocked_emails)

        # assertions
        mock_store_module_results_in_database.assert_called_once_with(
            target=self.test_target,
            results=self.mocked_emails,
            phase="recon",
            module="email_scraper",
        )
        assert mock_pass_results_in_email_scraper_module.call_count == len(
            self.mocked_emails
        )
