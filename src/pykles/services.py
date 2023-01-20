from pykles import logger, get_utc_timestamp
from pykles.kubernetes_functions import get_nodes, get_pod_metrics
from typing import Optional
from pykles.models import *
import json


def get_probe_status()->Ready:
    response_data = Ready(message='OK')
    logger.debug('respons_data={}'.format(response_data.dict()))
    return response_data


def get_pod_metrics_service()->GenericJson:
    # result = {
    #     'pod_metrics': get_pod_metrics(),
    # }
    return GenericJson(Data=get_pod_metrics())


def get_nodes_stats_service()->Nodes:
    nodes = Nodes(Nodes=list())
    for node_name, node_data in  get_nodes().items():
        cpu_capacity = node_data['Capacity']['CPU']
        cpu_allocatable = node_data['Allocatable']['CPU']
        cpu_commitment = node_data['Commitments']['CPU']
        cpu_commitment_percent = cpu_commitment / cpu_capacity * 100.0
        cpu_requests = node_data['Requests']['CPU']
        cpu_requests_percent = cpu_requests / cpu_capacity * 100.0

        ram_capacity = node_data['Capacity']['RAM']
        ram_allocatable = node_data['Allocatable']['RAM']
        ram_commitment = node_data['Commitments']['RAM']
        ram_commitment_percent = ram_commitment / ram_capacity * 100.0
        ram_requests = node_data['Requests']['RAM']
        ram_requests_percent = ram_requests / ram_capacity * 100.0

        nodes.nodes.append(
            Node(
                NodeName=node_name,
                CPU=Stats(
                    Capacity=cpu_capacity,
                    Allocatable=cpu_allocatable,
                    Requests=Values(
                        InstrumentedValue=cpu_requests,
                        Percent=cpu_requests_percent
                    ),
                    Limits=Values(
                        InstrumentedValue=cpu_commitment,
                        Percent=cpu_commitment_percent
                    )
                ),
                RAM=Stats(
                    Capacity=ram_capacity,
                    Allocatable=ram_allocatable,
                    Requests=Values(
                        InstrumentedValue=ram_requests,
                        Percent=ram_requests_percent
                    ),
                    Limits=Values(
                        InstrumentedValue=ram_commitment,
                        Percent=ram_commitment_percent
                    )
                )
            )
        )

    logger.debug('nodes={}'.format(vars(nodes)))
    return nodes



