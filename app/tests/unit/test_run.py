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

# skip B101

from unittest import mock

import pytest
from google.protobuf.timestamp_pb2 import Timestamp
from vehicle import vehicle  # type: ignore
from velocitas_sdk.vdb.types import TypedDataPointResult
from velocitas_sdk.vehicle_app import VehicleApp

MOCKED_SPEED = 0.0
MOCKED_LONGI_ACCEL = 0.0
MOCKED_LAT_ACCEL = 0.0
MOCKED_VER_ACCEL = 0.0


@pytest.mark.asyncio
async def test_for_get_speed():
    result = TypedDataPointResult("foo", MOCKED_SPEED, Timestamp(seconds=10, nanos=0))

    with mock.patch.object(
        vehicle.Speed,
        "get",
        new_callable=mock.AsyncMock,
        return_value=result,
    ):
        current_speed = (await vehicle.Speed.get()).value
        print(f"Received speed: {current_speed}")
        # Uncomment to test the behaviour of the SampleApp as provided by
        #     the template repository:
        # assert current_speed == MOCKED_SPEED


@pytest.mark.asyncio
async def test_for_get_longi_acceleration():
    result = TypedDataPointResult(
        "foo", MOCKED_LONGI_ACCEL, Timestamp(seconds=10, nanos=0)
    )

    with mock.patch.object(
        vehicle.Acceleration.Longitudinal,
        "get",
        new_callable=mock.AsyncMock,
        return_value=result,
    ):
        current_longi_acceleration = (
            await vehicle.Acceleration.Longitudinal.get()
        ).value
        print(f"Received Longitudinal acceleration: {current_longi_acceleration}")
        # Uncomment to test the behaviour of the SampleApp as provided by
        #     the template repository:
        # assert current_longi_acceleration == MOCKED_ACCELERATION


async def test_for_get_lateral_acceleration():
    result = TypedDataPointResult(
        "foo", MOCKED_LAT_ACCEL, Timestamp(seconds=10, nanos=0)
    )

    with mock.patch.object(
        vehicle.Acceleration.Lateral,
        "get",
        new_callable=mock.AsyncMock,
        return_value=result,
    ):
        current_lateral_acceleration = (await vehicle.Acceleration.Lateral.get()).value
        print(f"Received Lateral acceleration: {current_lateral_acceleration}")
        # Uncomment to test the behaviour of the SampleApp as provided by
        #     the template repository:
        # assert current_lateral_acceleration == MOCKED_LAT_ACCEL


@pytest.mark.asyncio
async def test_for_get_vertical_acceleration():
    result = TypedDataPointResult(
        "foo", MOCKED_VER_ACCEL, Timestamp(seconds=10, nanos=0)
    )

    with mock.patch.object(
        vehicle.Acceleration.Vertical,
        "get",
        new_callable=mock.AsyncMock,
        return_value=result,
    ):
        current_vertical_acceleration = (
            await vehicle.Acceleration.Vertical.get()
        ).value
        print(f"Received Vertical acceleration: {current_vertical_acceleration}")
        # Uncomment to test the behaviour of the SampleApp as provided by
        #     the template repository:
        # assert current_vertical_acceleration == MOCKED_VER_ACCEL


@pytest.mark.asyncio
async def test_for_publish_to_topic():
    with mock.patch.object(
        VehicleApp, "publish_mqtt_event", new_callable=mock.AsyncMock, return_value=-1
    ):
        response = await VehicleApp.publish_mqtt_event(
            str("sampleTopic"), get_sample_response_data()  # type: ignore
        )

        print(f"Received response: {response}")
        # Uncomment to test the behaviour of the SampleApp as provided by
        #     the template repository:
        # assert response == -1


def get_sample_response_data():
    return {
        "result": {
            "Speed_message": f"""Speed = {MOCKED_SPEED}""",
            "Longi_Accel_message": f"""Longitudinal Accel= {MOCKED_LONGI_ACCEL}""",
            "Lat_Accel_message": f"""Lateral Accel= {MOCKED_LAT_ACCEL}""",
            "Ver_Accel_message": f"""Vertical Accel= {MOCKED_VER_ACCEL}""",
        },
    }
