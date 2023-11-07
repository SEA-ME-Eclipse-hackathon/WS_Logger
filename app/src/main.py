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
from velocitas_sdk.vehicle_app import VehicleApp, subscribe_data_points, subscribe_topic

# Configure the VehicleApp logger with the necessary log config and level.
logging.setLogRecordFactory(get_opentelemetry_log_factory())
logging.basicConfig(format=get_opentelemetry_log_format())
logging.getLogger().setLevel("DEBUG")
logger = logging.getLogger(__name__)

SAFETY_FATAL_TOPIC = "safety/fatal"
LOGGER_LOG_TOPIC = "loggerapp/log"


class LoggerApp(VehicleApp):
    """
    This Logger logs vehicle information to log file
    It will be used to report to cloud
    """

    LOG_PATH = "./log/vehicle"
    LOG_FORMAT = "%(asctime)s [%(name)s]- %(message)s"

    def __init__(self, vehicle_client: Vehicle):
        # SampleApp inherits from VehicleApp.
        super().__init__()
        self.Vehicle = vehicle_client
        # set Logger
        os.makedirs(os.path.dirname(self.LOG_PATH), exist_ok=True)
        logFileHandler = TimedRotatingFileHandler(
            filename=self.LOG_PATH,
            when="s",
            interval=60,
            backupCount=5,
            encoding="UTF-8",
        )
        logFileHandler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        self.logger = logging.getLogger("VehicleSafetyLogger")
        self.logger.addHandler(logFileHandler)
        self.logger.setLevel("INFO")

    async def on_start(self):
        self.logger.info("LoggerApp started")
        return

    @subscribe_data_points("Vehicle.Speed")
    async def on_speed_change(self, data: DataPointReply):
        vehicle_speed = data.get(self.Vehicle.Speed).value
        self.logger.info(f"speed : {vehicle_speed}")

    @subscribe_topic(LOGGER_LOG_TOPIC)
    async def on_log(self, data: str):
        self.logger.info(str)


async def main():
    """Main function"""
    logger.info("Starting LoggerApp...")
    # Constructing SampleApp and running it.
    vehicle_app = LoggerApp(vehicle)
    await vehicle_app.run()


LOOP = asyncio.get_event_loop()
LOOP.add_signal_handler(signal.SIGTERM, LOOP.stop)
LOOP.run_until_complete(main())
LOOP.close()
