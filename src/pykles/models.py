import json
from typing import Optional
from pydantic import BaseModel, Field


class Values(BaseModel):
    instrument_value: float = Field(type=float, description='A measured or retrieved value', default=0.0, alias='InstrumentedValue')
    percent: float = Field(type=float, description='A measured or retrieved value expressed as a percentage of the total capacity available', default=0.0, alias='Percent')


class GenericJson(BaseModel):
    data: str = Field(type=str, description='A generic JSON data string', default='{}'.format(json.dumps(dict())), alias='Data')


class Stats(BaseModel):
    capacity: int = Field(type=int, description='Installed or provisioned capacity', default=0, alias='Capacity')
    allocatable: int = Field(type=int, description='Allocatable or available for use', default=0, alias='Allocatable')
    requests: Values = Field(
        type=Values,
        description='Amount of resources currently reserved (in use or requested)',
        default=Values(
            InstrumentedValue=0.0,
            Percent=0.0
        ),
        alias='Requests'
    )
    limits: Values = Field(
        type=Values,
        description='The maximum amount defined per all deployed resources as per their manifests',
        default=Values(
            InstrumentedValue=0.0,
            Percent=0.0
        ),
        alias='Limits'
    )


class Node(BaseModel):
    name: str = Field(type=str, description='The hostname of the node', default='localhost', alias='NodeName')
    cpu_stats: Stats = Field(
        type=Stats,
        description='CPU stats',
        default=Stats(
            Capacity=0.0,
            Allocatable=0.0,
            Requests=Values(
                InstrumentedValue=0.0,
                Percent=0.0
            ),
            Limits=Values(
                InstrumentedValue=0.0,
                Percent=0.0
            )
        ),
        alias='CPU'
    )
    ram_stats: Stats = Field(
        type=Stats,
        description='RAM stats',
        default=Stats(
            Capacity=0.0,
            Allocatable=0.0,
            Requests=Values(
                InstrumentedValue=0.0,
                Percent=0.0
            ),
            Limits=Values(
                InstrumentedValue=0.0,
                Percent=0.0
            )
        ),
        alias='RAM'
    )


class Nodes(BaseModel):
    nodes: list = Field(
        type=list,
        description='List of nodes with their stats',
        default=[
            Node(
                Name='localhost',
                CPU=Stats(
                    Capacity=0.0,
                    Allocatable=0.0,
                    Requests=Values(
                        InstrumentedValue=0.0,
                        Percent=0.0
                    ),
                    Limits=Values(
                        InstrumentedValue=0.0,
                        Percent=0.0
                    )
                ),
                RAM=Stats(
                    Capacity=0.0,
                    Allocatable=0.0,
                    Requests=Values(
                        InstrumentedValue=0.0,
                        Percent=0.0
                    ),
                    Limits=Values(
                        InstrumentedValue=0.0,
                        Percent=0.0
                    )
                )
            )
        ],
        alias='Nodes'
    )


class Ready(BaseModel):
    message: str = Field(type=str, description='The status of the application', default='OK', alias='Message')
    