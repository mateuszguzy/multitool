#!/bin/bash

monitor_directory() {
  local directory
  directory=$(pwd)

  inotifywait -r -m -e modify --format '%w%f' "$directory" |
    while read -r log_file_directory _ file; do
      tail_file "$log_file_directory" &
    done
}

tail_file() {
  local file="$1"
  tail -n 1 -f "$file"
}

monitor_directory
