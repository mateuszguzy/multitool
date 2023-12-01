import pytest

from modules.zap.context import (
    create_new_context,
    include_in_context,
    exclude_from_context,
    target_in_included_regexs,
    target_in_excluded_regexs,
)
from tests.conftest import CONTEXT_MODULE_PATH, TEST_TARGET


class TestContext:
    test_context_name = "test_context_name"
    test_target = TEST_TARGET
    module_path = CONTEXT_MODULE_PATH

    def test_create_new_context_success(self, mocker, mock_zap_context):
        mock_get_context_value = mocker.MagicMock()
        mocked_get_context = mocker.patch(
            f"{self.module_path}.get_context", return_value=mock_get_context_value
        )

        result = create_new_context(self.test_context_name)

        # assertions
        mock_zap_context.new_context.assert_called_once_with(self.test_context_name)
        mocked_get_context.assert_called_once_with(self.test_context_name)
        mock_get_context_value.get.assert_called_once()
        assert result == mock_get_context_value.get.return_value

    def test_create_new_context_fail(self, mocker, mock_zap_context):
        mocker.patch(f"{self.module_path}.get_context", side_effect=ValueError)

        with pytest.raises(ValueError):
            create_new_context(self.test_context_name)

    @pytest.mark.parametrize(
        "mocked_target_included_return_value, expected_call_count",
        [
            (True, 0),
            (False, 1),
        ],
    )
    def test_include_in_context_success(
        self,
        mocker,
        mocked_target_included_return_value,
        expected_call_count,
        mock_zap_context,
    ):
        mocked_target_included = mocker.patch(
            f"{self.module_path}.target_in_included_regexs",
            return_value=mocked_target_included_return_value,
        )
        mocker.patch(
            f"{self.module_path}.get_context", return_value=self.test_context_name
        )

        include_in_context(self.test_target, self.test_context_name)

        # assertions
        mocked_target_included.assert_called_once()
        assert mock_zap_context.include_in_context.call_count == expected_call_count

    def test_include_in_context_fail(self, mocker, mock_zap_context):
        mocker.patch(
            f"{self.module_path}.target_in_included_regexs", side_effect=ValueError
        )
        mocker.patch(
            f"{self.module_path}.get_context", return_value=self.test_context_name
        )

        with pytest.raises(ValueError):
            include_in_context(self.test_target, self.test_context_name)

    @pytest.mark.parametrize(
        "mocked_target_included_return_value, expected_call_count",
        [
            (True, 0),
            (False, 1),
        ],
    )
    def test_exclude_from_context_success(
        self,
        mocker,
        mocked_target_included_return_value,
        expected_call_count,
        mock_zap_context,
    ):
        mocked_target_included = mocker.patch(
            f"{self.module_path}.target_in_excluded_regexs",
            return_value=mocked_target_included_return_value,
        )
        mocker.patch(
            f"{self.module_path}.get_context", return_value=self.test_context_name
        )

        exclude_from_context([self.test_target], self.test_context_name)

        # assertions
        mocked_target_included.assert_called_once()
        assert mock_zap_context.exclude_from_context.call_count == expected_call_count

    def test_exclude_from_context_fail(self, mocker, mock_zap_context):
        mocker.patch(
            f"{self.module_path}.target_in_excluded_regexs", side_effect=ValueError
        )
        mocker.patch(
            f"{self.module_path}.get_context", return_value=self.test_context_name
        )

        with pytest.raises(ValueError):
            exclude_from_context(self.test_target, self.test_context_name)

    @pytest.mark.parametrize(
        "mocked_included_regexs, expected_return_value",
        [
            ([f"{TEST_TARGET}.*"], True),
            ([], False),
        ],
    )
    def test_target_in_included_regexs(
        self, mocker, mocked_included_regexs, expected_return_value
    ):
        mocker.patch(
            f"{self.module_path}.ast.literal_eval",
            return_value=mocked_included_regexs,
        )
        result = target_in_included_regexs(self.test_target, {})

        assert result == expected_return_value

    @pytest.mark.parametrize(
        "mocked_excluded_regexs, expected_return_value",
        [
            ([f"{TEST_TARGET}.*"], True),
            ([], False),
        ],
    )
    def test_target_in_excluded_regexs(
        self, mocker, mocked_excluded_regexs, expected_return_value
    ):
        mocker.patch(
            f"{self.module_path}.ast.literal_eval",
            return_value=mocked_excluded_regexs,
        )
        result = target_in_excluded_regexs(self.test_target, {})

        assert result == expected_return_value
