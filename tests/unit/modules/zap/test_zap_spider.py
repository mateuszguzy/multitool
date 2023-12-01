from config.settings import RECON_PHASE, ZAP_SPIDER
from modules.zap.zap_spider import save_zap_spider_results, start_zap_spider
from tests.conftest import ZAP_SPIDER_MODULE_PATH, TEST_TARGET


class TestZapSpider:
    module_path = ZAP_SPIDER_MODULE_PATH
    test_target = TEST_TARGET
    test_results = {"result1", "result2"}

    def test_start_zap_spider_success(
        self,
        mocker,
        mock_zap_spider,
        mock_log_results_in_zap_spider_module,
        mock_pass_result_event_in_zap_spider_module,
    ):
        mocker.patch(f"{self.module_path}.prepare_authentication_for_dvwa")
        mocked_log_results = mocker.patch(f"{self.module_path}.log_zap_spider_progress")
        mocked_zap_save_spider_results = mocker.patch(
            f"{self.module_path}.save_zap_spider_results"
        )
        mock_zap_spider.results.return_value = self.test_results

        start_zap_spider(target_url=self.test_target)

        # assertions
        mock_zap_spider.scan.assert_called_once()
        mocked_log_results.assert_called_once()
        mocked_zap_save_spider_results.assert_called_once()
        assert mock_pass_result_event_in_zap_spider_module.delay.call_count == len(
            self.test_results
        )
        assert mock_log_results_in_zap_spider_module.delay.call_count == len(
            self.test_results
        )

    def test_start_zap_spider_as_user_success(
        self,
        mocker,
        mock_zap_spider,
        mock_log_results_in_zap_spider_module,
        mock_pass_result_event_in_zap_spider_module,
    ):
        mocker.patch(f"{self.module_path}.prepare_authentication_for_dvwa")
        mocked_log_results = mocker.patch(f"{self.module_path}.log_zap_spider_progress")
        mocked_zap_save_spider_results = mocker.patch(
            f"{self.module_path}.save_zap_spider_results"
        )
        mocked_prepare_authentication_results = (mocker.MagicMock(), mocker.MagicMock())
        mocked_prepare_authentication = mocker.patch(
            f"{self.module_path}.prepare_authentication_for_dvwa",
            return_value=mocked_prepare_authentication_results,
        )
        mock_zap_spider.results.return_value = self.test_results

        start_zap_spider(target_url=self.test_target, as_user=True)

        # assertions
        mocked_prepare_authentication.assert_called_once()
        mock_zap_spider.scan_as_user.assert_called_once()
        mocked_log_results.assert_called_once()
        mocked_zap_save_spider_results.assert_called_once()
        assert mock_pass_result_event_in_zap_spider_module.delay.call_count == len(
            self.test_results
        )
        assert mock_log_results_in_zap_spider_module.delay.call_count == len(
            self.test_results
        )

    def test_save_zap_spider_results_success(self, mocker):
        mocked_convert_to_dict = mocker.patch(
            f"{self.module_path}.convert_list_or_set_to_dict",
            return_value=self.test_results,
        )
        mocked_store_in_db = mocker.patch(
            f"{self.module_path}.store_module_results_in_database"
        )

        save_zap_spider_results(self.test_results, self.test_target)

        # assertions
        mocked_convert_to_dict.assert_called_once_with(list_of_items=self.test_results)
        mocked_store_in_db.assert_called_once_with(
            target=self.test_target,
            results=self.test_results,
            phase=RECON_PHASE,
            module=ZAP_SPIDER,
        )
