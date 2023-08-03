import pytest


class TestCliInterface:
    """
    Test CLI Interface module.
    """

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.usefixtures("mock_click_prompt")
    @pytest.mark.parametrize(
        "test_input, expect",
        [
            ("a", "all"),
            ("A", "all"),
            ("sm", "single_module"),
            ("SM", "single_module"),
            ("sp", "single_phase"),
            ("SP", "single_phase"),
        ],
    )
    def test_use_type_question_success(self, test_input, expect, cli_interface):
        cli_interface.use_type_question()

        assert cli_interface.use_type == expect

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.usefixtures("mock_click_prompt")
    @pytest.mark.parametrize(
        "test_input, expect",
        [
            ("r", "recon"),
            ("R", "recon"),
        ],
    )
    def test_phase_question_success(self, test_input, expect, cli_interface):
        cli_interface.phase_question()

        assert cli_interface.phase == expect

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.usefixtures("mock_click_prompt")
    @pytest.mark.parametrize(
        "test_input, expect",
        [
            ("dirb", "directory_bruteforce"),
            ("DIRB", "directory_bruteforce"),
        ],
    )
    def test_module_question_success(self, test_input, expect, cli_interface):
        cli_interface.module_question()

        assert cli_interface.module == expect

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.usefixtures("mock_click_prompt")
    @pytest.mark.usefixtures("mock_clean_and_validate_input_targets")
    @pytest.mark.parametrize(
        "test_input, expect",
        [
            ("https://www.example.com:8080", "https://www.example.com:8080/"),
            ("https://www.example.com", "https://www.example.com/"),
            ("https://example.com", "https://example.com/"),
            ("https://example:8080", "https://example:8080/"),
            ("http://example.com", "http://example.com/"),
            ("http://example:8080", "http://example:8080/"),
            ("www.example.com", "http://www.example.com/"),
            ("http://example:8080, www.example.com", "http://example:8080/,http://www.example.com/"),

        ],
    )
    def test_targets_question_success(self, test_input, expect, cli_interface):
        cli_interface.targets_question()
        assert cli_interface.targets == expect.split(",")

        cli_interface.targets_helper_question()
        assert cli_interface.targets == expect.split(",")

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.usefixtures("mock_directory_bruteforce_questions")
    @pytest.mark.parametrize(
        "test_input, expect",
        [
            ("small", {"directory_bruteforce": {"list_size": "small"}}),
            ("medium", {"directory_bruteforce": {"list_size": "medium"}}),
            ("large", {"directory_bruteforce": {"list_size": "large"}}),
        ],
    )
    def test_recon_phase_questions_success(self, test_input, expect, cli_interface):
        cli_interface.directory_bruteforce_input = expect["directory_bruteforce"]
        cli_interface.recon_phase_questions()

        assert cli_interface.recon_phase_input == expect
