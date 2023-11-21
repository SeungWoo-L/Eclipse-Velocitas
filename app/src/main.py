# Copyright (c) 2022 Robert Bosch GmbH and Microsoft Corporation
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""A sample skeleton vehicle app."""
import asyncio
import json
import logging
import os
import signal
from logging.handlers import TimedRotatingFileHandler

from vehicle import Vehicle, vehicle  # type: ignore
from velocitas_sdk.util.log import (  # type: ignore
    get_opentelemetry_log_factory,
    get_opentelemetry_log_format,
)
from velocitas_sdk.vdb.reply import DataPointReply
from velocitas_sdk.vehicle_app import VehicleApp, subscribe_topic

# Logger setup
LOG_PATH = "logs/vehicle/app.log"

# Ensure the log directory exists
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# Logger names
SPEED_LOGGER_NAME = "vehicle/speed"
LONGI_ACCEL_LOGGER_NAME = "vehicle/acceleration_longitudinal"
LAT_ACCEL_LOGGER_NAME = "vehicle/acceleration_lateral"
VER_ACCEL_LOGGER_NAME = "vehicle/acceleration_vertical"

# Log format
LOG_FORMAT = "%(asctime)s [%(name)s]- %(message)s"

# MQTT topics
GET_SPEED_REQUEST_TOPIC = "sampleapp/getSpeed"
GET_SPEED_RESPONSE_TOPIC = "sampleapp/getSpeed/response"
DATABROKER_SPEED_SUBSCRIPTION_TOPIC = "sampleapp/currentSpeed"

GET_LONGI_ACCEL_REQUEST_TOPIC = "sampleapp/getLongitudinalAccel"
GET_LONGI_ACCEL_RESPONSE_TOPIC = "sampleapp/getLongitudinalAccel/response"
DATABROKER_LONGI_ACCEL_SUBSCRIPTION_TOPIC = "sampleapp/currentLongitudinalAccel"

GET_LAT_ACCEL_REQUEST_TOPIC = "sampleapp/getLateralAccel"
GET_LAT_ACCEL_RESPONSE_TOPIC = "sampleapp/getLateralAccel/response"
DATABROKER_LAT_ACCEL_SUBSCRIPTION_TOPIC = "sampleapp/currentLateralAccel"

GET_VER_ACCEL_REQUEST_TOPIC = "sampleapp/getVerticalAccel"
GET_VER_ACCEL_RESPONSE_TOPIC = "sampleapp/getVerticalAccel/response"
DATABROKER_VER_ACCEL_SUBSCRIPTION_TOPIC = "sampleapp/currentVerticalAccel"

# Configure the VehicleApp logger with the necessary log config and level
logging.setLogRecordFactory(get_opentelemetry_log_factory())
logging.basicConfig(format=get_opentelemetry_log_format())
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


# Helper function to set up loggers
def setup_accel_logger(logger_name):
    log_handler = TimedRotatingFileHandler(
        filename=LOG_PATH, when="s", interval=60, backupCount=5, encoding="utf-8"
    )
    log_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger = logging.getLogger(logger_name)
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    return logger


# Create loggers for each type of acceleration
SpeedLogger = setup_accel_logger(SPEED_LOGGER_NAME)
LongiAccelLogger = setup_accel_logger(LONGI_ACCEL_LOGGER_NAME)
LatAccelLogger = setup_accel_logger(LAT_ACCEL_LOGGER_NAME)
VerAccelLogger = setup_accel_logger(VER_ACCEL_LOGGER_NAME)


class SampleApp(VehicleApp):
    def __init__(self, vehicle_client: Vehicle):
        super().__init__()
        self.vehicle = vehicle_client

    async def on_start(self):
        await self.vehicle.Speed.subscribe(self.on_speed_change)
        await self.vehicle.Acceleration.Longitudinal.subscribe(self.on_accel_change)
        await self.vehicle.Acceleration.Lateral.subscribe(self.on_accel_change)
        await self.vehicle.Acceleration.Vertical.subscribe(self.on_accel_change)
        

    async def on_speed_change(self, data: DataPointReply):
        vehicle_speed = data.get(self.vehicle.Speed).value
        SpeedLogger.info("Vehicle speed: %s", vehicle_speed)
        await self.publish_event(
            DATABROKER_SPEED_SUBSCRIPTION_TOPIC, json.dumps({"speed": vehicle_speed})
        )

    async def on_accel_change(self, data: DataPointReply):
        vehicle_longi_accel = data.get(self.vehicle.Acceleration.Longitudinal).value
        vehicle_lat_acceleration = data.get(self.vehicle.Acceleration.Lateral).value
        vehicle_ver_acceleration = data.get(self.vehicle.Acceleration.Vertical).value

        LongiAccelLogger.info(
            "Vehicle longitudinal acceleration: %s", vehicle_longi_accel
        )
        LatAccelLogger.info(
            "Vehicle lateral acceleration: %s", vehicle_lat_acceleration
        )
        VerAccelLogger.info(
            "Vehicle vertical acceleration: %s", vehicle_ver_acceleration
        )

        # Publish each acceleration value to its respective topic
        await self.publish_event(
            DATABROKER_LONGI_ACCEL_SUBSCRIPTION_TOPIC,
            json.dumps({"longitudinal_acceleration": vehicle_longi_accel}),
        )
        await self.publish_event(
            DATABROKER_LAT_ACCEL_SUBSCRIPTION_TOPIC,
            json.dumps({"lateral_acceleration": vehicle_lat_acceleration}),
        )
        await self.publish_event(
            DATABROKER_VER_ACCEL_SUBSCRIPTION_TOPIC,
            json.dumps({"vertical_acceleration": vehicle_ver_acceleration}),
        )

    @subscribe_topic(GET_SPEED_REQUEST_TOPIC)
    async def on_get_speed_request_received(self, data: str):
        logger.debug(
            "Received speed request on topic %s with data: %s",
            GET_SPEED_REQUEST_TOPIC,
            data,
        )
        vehicle_speed = (await self.vehicle.Speed.get()).value
        await self.publish_event(
            GET_SPEED_RESPONSE_TOPIC,
            json.dumps(
                {"result": {"status": 0, "message": f"Speed = {vehicle_speed}"}}
            ),
        )

    @subscribe_topic(GET_LONGI_ACCEL_REQUEST_TOPIC)
    async def on_get_longi_accel_request_received(self, data: str):
        logger.debug(
            "Received longitudinal acceleration request on topic %s with data: %s",
            GET_LONGI_ACCEL_REQUEST_TOPIC,
            data,
        )
        vehicle_longi_accel = (await self.vehicle.Acceleration.Longitudinal.get()).value
        await self.publish_event(
            GET_LONGI_ACCEL_RESPONSE_TOPIC,
            json.dumps(
                {
                    "result": {
                        "status": 0,
                        "message": f"Longi Acceleration = {vehicle_longi_accel}",
                    }
                }
            ),
        )

    @subscribe_topic(GET_LAT_ACCEL_REQUEST_TOPIC)
    async def on_get_lat_accel_request_received(self, data: str):
        logger.debug(
            "Received lateral acceleration request on topic %s with data: %s",
            GET_LAT_ACCEL_REQUEST_TOPIC,
            data,
        )
        vehicle_lat_accel = (await self.vehicle.Acceleration.Lateral.get()).value
        await self.publish_event(
            GET_LAT_ACCEL_RESPONSE_TOPIC,
            json.dumps(
                {
                    "result": {
                        "status": 0,
                        "message": f"LAT Acceleration = {vehicle_lat_accel}",
                    }
                }
            ),
        )

    @subscribe_topic(GET_VER_ACCEL_REQUEST_TOPIC)
    async def on_get_ver_accel_request_received(self, data: str):
        logger.debug(
            "Received vertical acceleration request on topic %s with data: %s",
            GET_VER_ACCEL_REQUEST_TOPIC,
            data,
        )
        vehicle_ver_accel = (await self.vehicle.Acceleration.Vertical.get()).value
        await self.publish_event(
            GET_VER_ACCEL_RESPONSE_TOPIC,
            json.dumps(
                {
                    "result": {
                        "status": 0,
                        "message": f"Vertical Acceleration = {vehicle_ver_accel}",
                    }
                }
            ),
        )

    # Add similar methods for lateral and vertical acceleration requests


# Remaining async main and loop setup
async def main():
    logger.info("Starting SampleApp...")
    vehicle_app = SampleApp(vehicle)
    await vehicle_app.run()


LOOP = asyncio.get_event_loop()
LOOP.add_signal_handler(signal.SIGTERM, LOOP.stop)
LOOP.run_until_complete(main())
LOOP.close()
