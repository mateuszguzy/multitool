# Hacking MultiTool

> ⚠️ WORK IN PROGRESS...

## Manual
Currently, app is running against [DVWA](https://github.com/digininja/DVWA) for testing purposes. DVWM is run as a [Docker](https://www.docker.com/) container.

### Setup
Setup is required to be run only once, before running any other command. 
It's responsible for creating Docker container and installing all dependencies. First launch might take a while.
```bash
make build
```
Setup is launching app in multi-pane view.
```bash
make setup
```

### Running app
This command can be run multiple times, AFTER `make setup` is run.
```bash
make run
```

### Running tests
```bash
make test
```

### Stop the application
```bash
make stop
```
This stops Docker container running in the background.
