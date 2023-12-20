import pexpect  # type: ignore

from tests.conftest import (
    read_e2e_user_input_test_file_content,
    convert_json_input_to_dict,
    MOCK_USER_INPUT_ALL_1,
    target_list_to_string,
    MOCK_USER_INPUT_ALL_2,
    pexpect_child_cli_interface_test,
    MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE_1,
    MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE_2,
    MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_1,
    MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_2,
    MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_3,
    MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_4,
    MOCK_USER_INPUT_SINGLE_MODULE_ZAP_SPIDER_1,
    MOCK_USER_INPUT_SINGLE_MODULE_ZAP_SPIDER_2,
    MOCK_USER_INPUT_SINGLE_MODULE_ZAP_SPIDER_3,
    MOCK_USER_INPUT_SINGLE_PHASE_RECON_1,
    MOCK_USER_INPUT_SINGLE_PHASE_RECON_2,
    MOCK_USER_INPUT_SINGLE_PHASE_SCAN_1,
    MOCK_USER_INPUT_SINGLE_MODULE_LFI_1,
)


# FIXME: E2E tests work only run in PyCharm. Not in container, not in terminal.
class TestCliInterface:
    """
    Test the CLI interface by running the CLI interface questions script and mock user input.
    This test is not perfect due to the way 'Questionary' lib works.
    Main task of those tests is to verify if questions are following the correct dependency flow.

    NOTE: have to omit the 'Choose context file' question because it's not populating choices.

    NOTE 2: all tests need to have comments describing what option to what question is being selected, in form of:
    question_name: answer
    """

    up_arrow = "\033[A"
    down_arrow = "\033[B"

    def test_user_input_with_mocked_user_input_all_1(self, tmp_path):
        tmp_test_file_name = tmp_path / MOCK_USER_INPUT_ALL_1.split("/")[-1]
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)

        input_dict = convert_json_input_to_dict(MOCK_USER_INPUT_ALL_1)
        ports_as_string = target_list_to_string(
            input_dict["scan"]["port_scan"]["ports"]
        )

        # use_type: all
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # zap_spider_enhanced: False
        child.send("n")
        # zap_spider_as_user: False
        child.send("n")

        # directory_bruteforce_list_size: small
        child.sendline()
        # directory_bruteforce_recursive: False
        child.send("n")

        # port_scan_type: custom
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # ports_to_scan: 80, 443
        child.sendline(ports_as_string)

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert (
            file_content["zap_spider_enhanced"]
            == input_dict["recon"]["zap_spider"]["enhanced"]
        )
        assert (
            file_content["zap_spider_as_user"]
            == input_dict["recon"]["zap_spider"]["as_user"]
        )
        assert (
            file_content["directory_bruteforce_list_size"]
            == input_dict["recon"]["directory_bruteforce"]["list_size"]
        )
        assert (
            file_content["directory_bruteforce_recursive"]
            == input_dict["recon"]["directory_bruteforce"]["recursive"]
        )
        assert (
            file_content["port_scan_type"]
            == input_dict["scan"]["port_scan"]["port_scan_type"]
        )
        assert file_content["ports_to_scan"] == ports_as_string
        assert (
            file_content["output_after_every_finding"]
            == input_dict["output_after_every_finding"]
        )

    def test_user_input_with_mocked_user_input_all_2(self, tmp_path):
        tmp_test_file_name = tmp_path / MOCK_USER_INPUT_ALL_2.split("/")[-1]
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)
        input_dict = convert_json_input_to_dict(MOCK_USER_INPUT_ALL_2)

        # use_type: all
        child.sendline()
        # context: new
        child.sendline()
        # targets: https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # zap_spider_enhanced: True
        child.send("y")
        # zap_spider_as_user: True
        child.send("y")

        # directory_bruteforce_list_size: medium
        child.send(self.down_arrow)
        child.sendline()
        # directory_bruteforce_recursive: True
        child.send("y")

        # port_scan_type: custom
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()

        # output_after_every_finding: False
        child.send("n")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert (
            file_content["zap_spider_enhanced"]
            == input_dict["recon"]["zap_spider"]["enhanced"]
        )
        assert (
            file_content["zap_spider_as_user"]
            == input_dict["recon"]["zap_spider"]["as_user"]
        )
        assert (
            file_content["directory_bruteforce_list_size"]
            == input_dict["recon"]["directory_bruteforce"]["list_size"]
        )
        assert (
            file_content["directory_bruteforce_recursive"]
            == input_dict["recon"]["directory_bruteforce"]["recursive"]
        )
        assert (
            file_content["port_scan_type"]
            == input_dict["scan"]["port_scan"]["port_scan_type"]
        )
        assert (
            file_content["output_after_every_finding"]
            == input_dict["output_after_every_finding"]
        )

    def test_user_input_with_mocked_user_input_single_module_directory_bruteforce_1(
        self, tmp_path
    ):
        tmp_test_file_name = (
            tmp_path
            / MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE_1.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)
        input_dict = convert_json_input_to_dict(
            MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE_1
        )

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: recon
        child.sendline()

        # module: directory_bruteforce
        child.sendline()

        # directory_bruteforce_list_size: small
        child.sendline()
        # directory_bruteforce_recursive: False
        child.send("n")

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["directory_bruteforce_list_size"]
            == input_dict["recon"]["directory_bruteforce"]["list_size"]
        )
        assert (
            file_content["directory_bruteforce_recursive"]
            == input_dict["recon"]["directory_bruteforce"]["recursive"]
        )

    def test_user_input_with_mocked_user_input_single_module_directory_bruteforce_2(
        self, tmp_path
    ):
        tmp_test_file_name = (
            tmp_path
            / MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE_2.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)
        input_dict = convert_json_input_to_dict(
            MOCK_USER_INPUT_SINGLE_MODULE_DIRECTORY_BRUTEFORCE_2
        )

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: recon
        child.sendline()

        # module: directory_bruteforce
        child.sendline()

        # directory_bruteforce_list_size: medium
        child.send(self.down_arrow)
        child.sendline()
        # directory_bruteforce_recursive: True
        child.send("y")

        # output_after_every_finding: False
        child.send("n")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["directory_bruteforce_list_size"]
            == input_dict["recon"]["directory_bruteforce"]["list_size"]
        )
        assert (
            file_content["directory_bruteforce_recursive"]
            == input_dict["recon"]["directory_bruteforce"]["recursive"]
        )

    def test_user_input_with_mocked_user_input_single_module_port_scan_1(
        self, tmp_path
    ):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_1.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)
        input_dict = convert_json_input_to_dict(
            MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_1
        )
        ports_as_string = target_list_to_string(
            input_dict["scan"]["port_scan"]["ports"]
        )

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: scan
        child.send(self.down_arrow)
        child.sendline()

        # module: port_scan
        child.sendline()

        # port_scan_type: custom
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # ports_to_scan: [80, 443]
        child.sendline(ports_as_string)

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["port_scan_type"]
            == input_dict["scan"]["port_scan"]["port_scan_type"]
        )
        assert file_content["ports_to_scan"] == ports_as_string

    def test_user_input_with_mocked_user_input_single_module_port_scan_2(
        self, tmp_path
    ):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_2.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)
        input_dict = convert_json_input_to_dict(
            MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_2
        )

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: scan
        child.send(self.down_arrow)
        child.sendline()

        # module: port_scan
        child.sendline()

        # port_scan_type: important
        child.sendline()

        # output_after_every_finding: False
        child.send("n")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["port_scan_type"]
            == input_dict["scan"]["port_scan"]["port_scan_type"]
        )

    def test_user_input_with_mocked_user_input_single_module_port_scan_3(
        self, tmp_path
    ):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_3.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)
        input_dict = convert_json_input_to_dict(
            MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_3
        )

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: scan
        child.send(self.down_arrow)
        child.sendline()

        # module: port_scan
        child.sendline()

        # port_scan_type: top_1000
        child.send(self.down_arrow)
        child.sendline()

        # output_after_every_finding: False
        child.send("n")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["port_scan_type"]
            == input_dict["scan"]["port_scan"]["port_scan_type"]
        )

    def test_user_input_with_mocked_user_input_single_module_port_scan_4(
        self, tmp_path
    ):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_4.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)
        input_dict = convert_json_input_to_dict(
            MOCK_USER_INPUT_SINGLE_MODULE_PORT_SCAN_4
        )

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: scan
        child.send(self.down_arrow)
        child.sendline()

        # module: port_scan
        child.sendline()

        # port_scan_type: all
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()

        # output_after_every_finding: False
        child.send("n")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["port_scan_type"]
            == input_dict["scan"]["port_scan"]["port_scan_type"]
        )

    def test_user_input_with_mocked_user_input_single_module_zap_spider_1(
        self, tmp_path
    ):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_MODULE_ZAP_SPIDER_1.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)

        input_dict = convert_json_input_to_dict(
            MOCK_USER_INPUT_SINGLE_MODULE_ZAP_SPIDER_1
        )

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: recon
        child.sendline()

        # module: zap_spider
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()

        # zap_spider_enhanced: False
        child.send("n")
        # zap_spider_as_user: False
        child.send("n")

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["zap_spider_enhanced"]
            == input_dict["recon"]["zap_spider"]["enhanced"]
        )
        assert (
            file_content["zap_spider_as_user"]
            == input_dict["recon"]["zap_spider"]["as_user"]
        )
        assert (
            file_content["output_after_every_finding"]
            == input_dict["output_after_every_finding"]
        )

    def test_user_input_with_mocked_user_input_single_module_zap_spider_2(
        self, tmp_path
    ):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_MODULE_ZAP_SPIDER_2.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)

        input_dict = convert_json_input_to_dict(
            MOCK_USER_INPUT_SINGLE_MODULE_ZAP_SPIDER_2
        )

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: recon
        child.sendline()

        # module: zap_spider
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()

        # zap_spider_enhanced: True
        child.send("y")
        # zap_spider_as_user: False
        child.send("n")

        # directory_bruteforce_list_size: small
        child.sendline()
        # directory_bruteforce_recursive: False
        child.send("n")

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["zap_spider_enhanced"]
            == input_dict["recon"]["zap_spider"]["enhanced"]
        )
        assert (
            file_content["zap_spider_as_user"]
            == input_dict["recon"]["zap_spider"]["as_user"]
        )
        assert (
            file_content["directory_bruteforce_list_size"]
            == input_dict["recon"]["directory_bruteforce"]["list_size"]
        )
        assert (
            file_content["directory_bruteforce_recursive"]
            == input_dict["recon"]["directory_bruteforce"]["recursive"]
        )
        assert (
            file_content["output_after_every_finding"]
            == input_dict["output_after_every_finding"]
        )

    def test_user_input_with_mocked_user_input_single_module_zap_spider_3(
        self, tmp_path
    ):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_MODULE_ZAP_SPIDER_3.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)

        input_dict = convert_json_input_to_dict(
            MOCK_USER_INPUT_SINGLE_MODULE_ZAP_SPIDER_3
        )

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: recon
        child.sendline()

        # module: zap_spider
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()

        # zap_spider_enhanced: False
        child.send("n")
        # zap_spider_as_user: True
        child.send("y")

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["zap_spider_enhanced"]
            == input_dict["recon"]["zap_spider"]["enhanced"]
        )
        assert (
            file_content["zap_spider_as_user"]
            == input_dict["recon"]["zap_spider"]["as_user"]
        )
        assert (
            file_content["output_after_every_finding"]
            == input_dict["output_after_every_finding"]
        )

    def test_user_input_with_mocked_user_input_single_module_lfi_1(self, tmp_path):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_MODULE_LFI_1.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)

        input_dict = convert_json_input_to_dict(MOCK_USER_INPUT_SINGLE_MODULE_LFI_1)

        # use_type: single_module
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: gain_access
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()

        # module: lfi
        child.sendline()

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert file_content["module"] == input_dict["module"]
        assert (
            file_content["output_after_every_finding"]
            == input_dict["output_after_every_finding"]
        )

    def test_user_input_with_mocked_user_input_single_phase_recon_1(self, tmp_path):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_PHASE_RECON_1.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)

        input_dict = convert_json_input_to_dict(MOCK_USER_INPUT_SINGLE_PHASE_RECON_1)

        # use_type: single_phase
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: recon
        child.sendline()

        # zap_spider_enhanced: False
        child.send("n")
        # zap_spider_as_user: False
        child.send("n")

        # directory_bruteforce_list_size: small
        child.sendline()
        # directory_bruteforce_recursive: False
        child.send("n")

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert (
            file_content["zap_spider_enhanced"]
            == input_dict["recon"]["zap_spider"]["enhanced"]
        )
        assert (
            file_content["zap_spider_as_user"]
            == input_dict["recon"]["zap_spider"]["as_user"]
        )
        assert (
            file_content["directory_bruteforce_list_size"]
            == input_dict["recon"]["directory_bruteforce"]["list_size"]
        )
        assert (
            file_content["directory_bruteforce_recursive"]
            == input_dict["recon"]["directory_bruteforce"]["recursive"]
        )
        assert (
            file_content["output_after_every_finding"]
            == input_dict["output_after_every_finding"]
        )

    def test_user_input_with_mocked_user_input_single_phase_recon_2(self, tmp_path):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_PHASE_RECON_2.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)

        input_dict = convert_json_input_to_dict(MOCK_USER_INPUT_SINGLE_PHASE_RECON_2)

        # use_type: single_phase
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: recon
        child.sendline()

        # zap_spider_enhanced: True
        child.send("y")
        # zap_spider_as_user: False
        child.send("n")

        # directory_bruteforce_list_size: medium
        child.send(self.down_arrow)
        child.sendline()
        # directory_bruteforce_recursive: True
        child.send("y")

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert (
            file_content["zap_spider_enhanced"]
            == input_dict["recon"]["zap_spider"]["enhanced"]
        )
        assert (
            file_content["zap_spider_as_user"]
            == input_dict["recon"]["zap_spider"]["as_user"]
        )
        assert (
            file_content["directory_bruteforce_list_size"]
            == input_dict["recon"]["directory_bruteforce"]["list_size"]
        )
        assert (
            file_content["directory_bruteforce_recursive"]
            == input_dict["recon"]["directory_bruteforce"]["recursive"]
        )
        assert (
            file_content["output_after_every_finding"]
            == input_dict["output_after_every_finding"]
        )

    def test_user_input_with_mocked_user_input_single_phase_scan_1(self, tmp_path):
        tmp_test_file_name = (
            tmp_path / MOCK_USER_INPUT_SINGLE_PHASE_SCAN_1.split("/")[-1]
        )
        child = pexpect_child_cli_interface_test(tmp_file_path=tmp_test_file_name)

        input_dict = convert_json_input_to_dict(MOCK_USER_INPUT_SINGLE_PHASE_SCAN_1)
        ports_as_string = target_list_to_string(
            input_dict["scan"]["port_scan"]["ports"]
        )

        # use_type: single_phase
        child.send(self.down_arrow)
        child.sendline()
        # context: new
        child.sendline()
        # targets: http://dvwa/, https://www.example.com
        child.sendline(target_list_to_string(input_dict["targets"]))
        # exclude_targets: []
        child.sendline()

        # phase: scan
        child.send(self.down_arrow)
        child.sendline()

        # port_scan_type: custom
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.send(self.down_arrow)
        child.sendline()
        # ports_to_scan: 80, 443
        child.sendline(ports_as_string)

        # output_after_every_finding: True
        child.send("y")

        # end of questions
        child.expect_exact(pexpect.EOF)

        file_content = read_e2e_user_input_test_file_content(
            filename=tmp_test_file_name
        )
        assert file_content["use_type"] == input_dict["use_type"]
        # param omitted
        assert file_content.get("context_file_name", None) is None
        assert file_content["exclude_targets"] == ""
        assert file_content["phase"] == input_dict["phase"]
        assert (
            file_content["port_scan_type"]
            == input_dict["scan"]["port_scan"]["port_scan_type"]
        )
        assert file_content["ports_to_scan"] == ports_as_string
        assert (
            file_content["output_after_every_finding"]
            == input_dict["output_after_every_finding"]
        )
