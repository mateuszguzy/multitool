import json
import sys

sys.path.append(".")


from modules.user_interface.cli.cli_interface import CliInterface


def run_cli_interface_questions_prompt():
    user_input = CliInterface().ask_questions()
    tmp_file_path = sys.argv[-1]

    with open(f"{tmp_file_path}", "w") as f:
        json.dump(user_input, f)


if __name__ == "__main__":
    run_cli_interface_questions_prompt()
