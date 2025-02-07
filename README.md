# Fritz to MQTT

## Description
This project is a proof of concept to interact with FritzBox routers and publish the data of found WiFi networks to an MQTT broker.

## Project Structure
```
my-python-project/
├── Dockerfile           # Dockerfile to build the Docker image
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # List of dependencies
├── setup.py             # Packaging configuration
├── sid.json             # File to store the SID
├── config.ini.example   # Example configuration file
├── .env.example         # Example environment variables file
├── app.log              # Log file
├── LICENSE
└── src/
    └── main.py          # Main application code
└── doc/                 # Documentation files

```

## Installation
To install the required dependencies, run the following command:
```sh
pip install -r requirements.txt
```

## Configuration
The `config.ini` file is required only if the software is to be run without a Docker container. When running the application inside a Docker container, the `.env` file is used instead.

Make sure you have a `config.ini` file in the project's root directory with the following content:
```ini
[DEFAULT]
FRITZBOX_URL = http://192.168.1.1
USERNAME = your_username
PASSWORD = your_password
SID_FILE = sid.json
LOG_FILE = app.log
LOOP_TIMEOUT = 30
MQTT_BROKER = your_mqtt_broker_ip
MQTT_PORT = 1883
MQTT_USERNAME = your_mqtt_username
MQTT_PASSWORD = your_mqtt_password
MQTT_BASE_TOPIC = home/fritzbox/wifi
```

Additionally, create a `.env` file in the project's root directory by renaming the `.env.example` file and updating the values as needed. This file is used to set environment variables for the Docker container, so it should be modified only if you are running the application in this mode:
```sh
mv .env.example .env
```
```
FRITZBOX_URL=http://192.168.1.1
USERNAME=your_username
PASSWORD=your_password
SID_FILE=sid.json
LOG_FILE=app.log
LOOP_TIMEOUT=30
MQTT_BROKER=your_mqtt_broker_ip
MQTT_PORT=1883
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password
MQTT_BASE_TOPIC=home/fritzbox/wifi
```

## Usage
To run the application, execute the following command:
```sh
python src/main.py
```

### Usage with Docker
To run the application using Docker, follow these steps:

Build the Docker image and run the container using Docker Compose:
```sh
docker-compose -f 'docker-compose.yml' up -d --build
```

Check the Docker container logs to ensure the application is running correctly:
```sh
docker logs fritzbox_parser
```


### Debugging with Docker Compose
To debug the application using Docker Compose, you can use the following configurations in your `.vscode/launch.json` file:

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.