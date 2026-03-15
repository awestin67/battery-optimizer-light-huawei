# Gemini Code Assistant Context

This document provides context for the Gemini AI code assistant to understand and effectively assist with the development of the **Battery Optimizer Light Huawei** Home Assistant integration.

## Project Overview

This is a custom component for Home Assistant that provides lightweight control for **Huawei Luna2000** batteries. It is designed to work in tandem with the official `Huawei Solar` integration and another custom integration, `Battery Optimizer Light`.

The primary goal of this integration is to act on decisions made by `Battery Optimizer Light` to control the battery's charging, discharging, and operating mode.

### Core Technologies

-   **Language:** Python 3
-   **Framework:** Home Assistant Integration
-   **Primary Domain:** `battery_optimizer_light_huawei`

### Key Features

-   **Sensors:**
    -   `binary_sensor`: Tracks the connection status to the Huawei Solar API.
    -   `sensor`: Mirrors the current working mode and device status of the Huawei inverter.
-   **Services:**
    -   Provides services (`force_charge`, `force_discharge`, `hold`, `auto`) to control the battery. These services call the underlying services of the `Huawei Solar` integration.

## Building and Running

This is a Home Assistant integration and is meant to be run within a Home Assistant instance.

### Dependencies

-   **Runtime:** None specified in `manifest.json`, but it has a dependency on the `Huawei Solar` integration being installed in Home Assistant.
-   **Test:**
    -   `pytest`
    -   `pytest-asyncio`
    -   `aiohttp`

### Running Tests

Tests are run using `pytest`. Based on the `pyproject.toml`, the asyncio mode is set to `auto`.

To run the tests, execute the following command:

```bash
pytest
```

## Development Conventions

### Linting and Formatting

The project uses `Ruff` for linting. The configuration is located in `pyproject.toml`.

-   **Line length:** 120 characters
-   **Selected rules:** `E`, `F`, `W`, `B`

To run the linter, you can use the following command:

```bash
ruff check .
```

### Code Style

-   The code follows standard Python and Home Assistant conventions.
-   The primary language for user-facing text (as seen in `README.md` and `strings.json`) is Swedish.

## Project Structure

-   `.github/workflows/`: Contains CI/CD workflows for linting, testing, and validation.
-   `custom_components/battery_optimizer_light_huawei/`: The main source code for the integration.
    -   `__init__.py`: Integration setup and service registration.
    -   `binary_sensor.py`: Platform setup for binary sensors.
    -   `sensor.py`: Platform setup for sensors.
    -   `config_flow.py`: Handles the configuration flow for the integration.
    -   `const.py`: Contains constants for the integration domain, configuration keys, etc.
    -   `manifest.json`: Integration metadata, including domain, name, version, and dependencies.
    -   `services.yaml`: Defines the custom services offered by the integration.
    -   `translations/`: Contains localization files (e.g., `en.json`, `sv.json`).
-   `tests/`: Contains pytest tests for the integration.
-   `hacs.json`: Configuration file for the Home Assistant Community Store (HACS).
-   `pyproject.toml`: Project configuration, including settings for `Ruff` and `pytest`.
-   `README.md`: Project documentation in Swedish.
