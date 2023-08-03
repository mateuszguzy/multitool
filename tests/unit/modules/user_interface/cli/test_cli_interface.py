import pytest


class TestCliInterface:
    """
    Test CLI Interface module.
    """

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.usefixtures("mock_click_prompt_without_return_value")
    @pytest.mark.usefixtures("mock_translate_abbreviations")
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
    @pytest.mark.usefixtures("mock_click_prompt_without_return_value")
    @pytest.mark.usefixtures("mock_translate_abbreviations")
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
    @pytest.mark.usefixtures("mock_click_prompt_without_return_value")
    @pytest.mark.usefixtures("mock_translate_abbreviations")
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
    @pytest.mark.usefixtures("mock_click_prompt_without_return_value")
    @pytest.mark.usefixtures("mock_clean_and_validate_input_targets")
    @pytest.mark.parametrize(
        "test_input, expect",
        [
            ("https://www.example.com:8080", ["https://www.example.com:8080/"]),
            ("https://www.example.com", ["https://www.example.com/"]),
            ("https://example.com", ["https://example.com/"]),
            ("https://example:8080", ["https://example:8080/"]),
            ("http://example.com", ["http://example.com/"]),
            ("http://example:8080", ["http://example:8080/"]),
            ("www.example.com", ["http://www.example.com/"]),
            ("http://example:8080, www.example.com", ["http://example:8080/", "http://www.example.com/"]),

        ],
    )
    def test_targets_question_success(self, test_input, expect, cli_interface):
        cli_interface.targets_question()
        assert cli_interface.targets == expect

        cli_interface.targets_helper_question()
        assert cli_interface.targets == expect

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

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.usefixtures("mock_directory_bruteforce_list_size_question")
    @pytest.mark.parametrize(
        "test_input, expect",
        [
            ("small", {"list_size": "small"}),
            ("medium", {"list_size": "medium"}),
            ("large", {"list_size": "large"}),
        ],
    )
    def test_directory_bruteforce_questions_success(self, test_input, expect, cli_interface):
        cli_interface.directory_bruteforce_list_size = test_input
        cli_interface.directory_bruteforce_questions()

        assert cli_interface.directory_bruteforce_input == expect

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.usefixtures("mock_click_prompt_with_return_value")
    @pytest.mark.parametrize(
        "test_input, expect",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_output_after_every_phase_question_success(self, test_input, expect, cli_interface):
        cli_interface.output_after_every_phase_question()

        assert cli_interface.output_after_every_phase == expect

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.usefixtures("mock_click_prompt_with_return_value")
    @pytest.mark.parametrize(
        "test_input, expect",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_output_after_every_finding_question_success(self, test_input, expect, cli_interface):
        cli_interface.output_after_every_finding_question()

        assert cli_interface.output_after_every_finding == expect

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.parametrize(
        "test_input_key, test_input_abbrev, expect",
        [
            ("use_type", "a", "all"),
            ("use_type", "A", "all"),
            ("use_type", "sp", "single_phase"),
            ("use_type", "SP", "single_phase"),
            ("use_type", "sm", "single_module"),
            ("use_type", "SM", "single_module"),
            ("phase", "r", "recon"),
            ("phase", "R", "recon"),
            ("module", "dirb", "directory_bruteforce"),
            ("module", "DIRB", "directory_bruteforce"),
            ("wordlist_size", "s", "small"),
            ("wordlist_size", "S", "small"),
            ("wordlist_size", "m", "medium"),
            ("wordlist_size", "M", "medium"),
            ("wordlist_size", "t", "test"),
            ("wordlist_size", "T", "test"),
        ]
    )
    def test_translate_abbreviations_success(self, test_input_key, test_input_abbrev, expect, cli_interface):
        result = cli_interface._translate_abbreviations(key=test_input_key, abbreviation=test_input_abbrev)

        assert result == expect

    @pytest.mark.usefixtures("cli_interface")
    @pytest.mark.parametrize(
        "test_input_key, test_input_abbrev, expect",
        [
            ("use_type", "all", ""),
            ("use_type", "single", ""),
            ("use_type", "phase", ""),
            ("use_type", "single_module", ""),
            ("phase", "recon", ""),
            ("module", "directory_bruteforce", ""),
            ("module", "port_scan", ""),
            ("wordlist_size", "l", ""),
            ("wordlist_size", "medium", ""),
            ("wordlist_size", "test", ""),
            ("wordlist_size", "large", ""),
        ]
    )
    def test_translate_abbreviations_fail(self, test_input_key, test_input_abbrev, expect, cli_interface):
        with pytest.raises(KeyError):
            cli_interface._translate_abbreviations(key=test_input_key, abbreviation=test_input_abbrev)
