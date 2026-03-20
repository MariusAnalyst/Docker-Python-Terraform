import json
import dataclasses

from dataclasses import dataclass


@dataclass
class Ride:
    PULocationID: int
    DOLocationID: int
    trip_distance: float
    total_amount: float
    lpep_pickup_datetime: int  # epoch milliseconds
    lpep_dropoff_datetime: int
    passenger_count: int
    tip_amount: int



def ride_from_row(row):
    return Ride(
        lpep_pickup_datetime = int(row['lpep_pickup_datetime'].timestamp() * 1000),
        lpep_dropoff_datetime = int(row['lpep_dropoff_datetime'].timestamp() * 1000),
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        passenger_count=float(row['passenger_count']),
        trip_distance=float(row['trip_distance']),
        tip_amount=float(row['tip_amount']),
        total_amount=float(row['total_amount'])

    )


def ride_serializer(ride):
    ride_dict = dataclasses.asdict(ride)
    ride_json = json.dumps(ride_dict).encode('utf-8')
    return ride_json


def ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return Ride(**ride_dict)