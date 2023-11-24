from tests.conftest import TEST_TARGET, LFI_MODULE_PATH


class TestLocalFileInclusion:
    module_path = LFI_MODULE_PATH
    test_target = TEST_TARGET
    file_path = "/etc/passwd"
    current_query = "filename=test.txt"
    mocked_result = ["user1", "user2"]

    def test_run_success(self, mocker, local_file_inclusion_fixture):
        mocker.patch(f"{self.module_path}.urlparse", return_value=mocker.MagicMock())
        mocker.patch(
            f"{self.module_path}.LocalFileInclusion._make_request", return_value=False
        )

        lfi = local_file_inclusion_fixture
        lfi.run()

        assert lfi._make_request.call_count == 6
        assert lfi._make_request.call_args_list == [
            mocker.call(parsed_url=mocker.ANY, query=mocker.ANY),
            mocker.call(parsed_url=mocker.ANY, query=mocker.ANY),
            mocker.call(parsed_url=mocker.ANY, query=mocker.ANY),
            mocker.call(parsed_url=mocker.ANY, query=mocker.ANY),
            mocker.call(parsed_url=mocker.ANY, query=mocker.ANY),
            mocker.call(parsed_url=mocker.ANY, query=mocker.ANY),
        ]

    def test_make_request_success(
        self,
        mocker,
        local_file_inclusion_fixture,
        mock_lfi_web_request,
        mock_lfi_module_pass_results,
        mock_lfi_module_save_module_results,
    ):
        mocker.patch(f"{LFI_MODULE_PATH}.urlunparse", return_value=self.test_target)
        mocker.patch(
            f"{LFI_MODULE_PATH}.extract_passwd_file_content_from_web_response",
            return_value=self.mocked_result,
        )

        lfi = local_file_inclusion_fixture
        lfi._make_request(parsed_url=mocker.MagicMock(), query=self.current_query)

        assert mock_lfi_web_request.call_count == 1
        assert mock_lfi_web_request.call_args == mocker.call(
            request_method="GET", target=self.test_target, allow_redirects=True
        )
        assert lfi._pass_results.call_count == 1
        assert lfi._pass_results.call_args == mocker.call(results=self.mocked_result)
        assert lfi._save_module_results.call_count == 1
        assert lfi._save_module_results.call_args == mocker.call(
            results=self.mocked_result
        )

    def test_run_with_finding_after_first_method_success(
        self, mocker, local_file_inclusion_fixture
    ):
        mocker.patch(f"{self.module_path}.urlparse", return_value=mocker.MagicMock())
        mocker.patch(
            f"{self.module_path}.LocalFileInclusion._make_request", return_value=True
        )

        lfi = local_file_inclusion_fixture
        lfi.run()

        assert lfi._make_request.call_count == 1
        assert lfi._make_request.call_args_list == [
            mocker.call(parsed_url=mocker.ANY, query=mocker.ANY),
        ]

    def test_absolute_path_bypass_success(self, local_file_inclusion_fixture):
        lfi = local_file_inclusion_fixture
        expected_result = f"filename=/../../../../../..{self.file_path}"

        result = lfi._absolute_path_bypass(self.file_path, self.current_query)

        assert result == expected_result

    def test_start_path_validation_bypass_success(self, local_file_inclusion_fixture):
        lfi = local_file_inclusion_fixture
        expected_result = f"filename=/var/www/images/../../../../../..{self.file_path}"

        result = lfi._start_path_validation_bypass(self.file_path, self.current_query)

        assert result == expected_result

    def test_extension_validation_bypass_success(self, local_file_inclusion_fixture):
        lfi = local_file_inclusion_fixture
        expected_result = f"filename=/../../../../../..{self.file_path}%00"

        result = lfi._extension_validation_bypass(self.file_path, self.current_query)

        assert result == expected_result
