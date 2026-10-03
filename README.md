# awox-connect-wifi

Python application to control AwoX Connect Wi-Fi smart devices.

> [!WARNING]
> ## Disclaimer
>
> This application is not authorized, endorsed, or officially supported by AwoX.
>
> Some IDs and keys used by this application were obtained from the Android application, while others were inferred or
experimentally determined.
>
> This project should be considered experimental and may not work reliably with all devices or firmware versions.
>
> Some parts of the code were generated with the assistance of AI. Although the code has been manually reviewed and
> tested, bugs and unexpected behavior may still be present.

> [!CAUTION]
> Limited testing
>
> This application has only been tested with a single EGLOBulb+ smart light .
>
> Compatibility with other EGLO products, bulbs, bridges, firmware versions, or device configurations has not been
verified and may require additional work.

## Installation

Clone the repository and install the project using the included pyproject.toml:

```
git clone https://github.com/Pierre-TELLIER/awox-connect-wifi
cd awox-connect-wifi
python3 -m pip install .
```

## Configuration

Configuration is loaded from environment variables.

Start by copying the example configuration:

```
cp config/.env.example config/.env
```

Then edit .env and provide the required values.

> [!WARNING]
> Do not commit your .env file or any credentials, certificates, keys, or other sensitive information to the repository.

## Usage

The application is launched as a Python module:

```
python3 -m awox.cli
```

There are multiple options

```
-d, --device DEVICE       Set selected device ID (you can get it by running without args). It is required for other commands to work
--on                      Turn the device on 
--off                     Turn the device off
-b, --brightness 0-100    Set brightness
-t, --temperature 0-100   Set color temperature
-c, --color R,G,B         Set RGB color
--reprovision             Restart device provisioning
```

The CLI handles the device connection and communication with the AwoX service.

## Protocol

The AwoX communication protocol was reverse engineered from the Android application.

The MQTT topics, message formats, authentication flow, and device communication ~~are~~ will maybe be documented in
`technical.md`

## Project Status

This project is experimental and under *more or less* active development.

At the moment, functionality and compatibility have only been verified against the specific EGLO Bulb+ setup used during
development. Other devices may expose different capabilities or behave differently.

Contributions, testing with other devices, and protocol observations are welcome.

## Acknowledgement

This work is based on [fsaris](https://github.com/fsaris/home-assistant-awox) repo for some part of the authentification 
