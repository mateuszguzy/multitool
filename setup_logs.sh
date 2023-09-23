#!/bin/bash

MODULES=$(grep -o "RESULTS_FOR_USER_FROM_MODULES = \[\(.*\)\]" config/settings.py | cut -d "[" -f2 | cut -d "]" -f1 | tr -d " '")
CURRENT_DATE=$(date -u +'%Y%m%d')
MULTITAIL_COMMAND_STRING="multitail "
LOGGING_DIR="./logs/${CURRENT_DATE}"

run_multitail() {
  sh -c "$MULTITAIL_COMMAND_STRING"
}

prepare_multitail_command() {
  for module in ${MODULES//,/ }; do
      module=$(echo "$module" | tr -d '"' | tr '[:upper:]' '[:lower:]')
      filename="${CURRENT_DATE}_${module}.log"
      mkdir -p "${LOGGING_DIR}"
      touch "${LOGGING_DIR}/${filename}" &>/dev/null
      # show every change in modules log files in console
      # to be changed when results showing based on user input will be implemented
      MULTITAIL_COMMAND_STRING+="-n 0 -f ${LOGGING_DIR}/${filename} "  # ! important whitespace at the end
  done
}

run_multi_pane_view() {
  # Start a new tmux session with two windows
  tmux new-session -d -s multitool_session

  # Create new window and run 'multitail' in it
  tmux new-window "${MULTITAIL_COMMAND_STRING}"
  # Split this window to show bare shell
  tmux split-window -h
  # Swap locations of panes (by default bare shell will be on right hand side)
  tmux swap-pane -D

  # Attach to the tmux session
  tmux attach-session -t multitool_session
}

prepare_multitail_command
run_multi_pane_view


