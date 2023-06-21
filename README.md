# Hacking MultiTool

## Manual
### Setup
Currently, app is running against [DVWA](https://github.com/digininja/DVWA) for testing purposes. DVWM is run as a [Docker](https://www.docker.com/) container.
```bash
make setup
```
Setup is required to be run only once, before running any other command.

### Running app
This command can be run multiple times, AFTER `make setup` is run.
```bash
make run
```

### Running application tests
```bash
make test
```

### Stop the application
```bash
make stop
```
This stops Docker container running in the background.
