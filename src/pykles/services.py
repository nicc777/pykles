from pykles import logger, get_utc_timestamp
from pykles.kubernetes_functions import get_nodes
from typing import Optional
from pykles.models import *


def get_probe_status()->Ready:
    response_data = Ready(message='OK')
    logger.debug('respons_data={}'.format(response_data.dict()))
    return response_data


def get_nodes_stats_service()->Nodes:
    nodes = Nodes(Nodes=list())
    for node_name, node_data in  get_nodes().items():
        cpu_capacity = node_data['Capacity']['CPU']
        cpu_commitment = node_data['Commitments']['CPU']
        ram_capacity = node_data['Capacity']['RAM']
        ram_commitment = node_data['Commitments']['RAM']
        cpu_commitment_percent = cpu_commitment / cpu_capacity * 100.0
        ram_commitment_percent = ram_commitment / ram_capacity * 100.0

        nodes.nodes.append(
            Node(
                NodeName=node_name,
                CPU=Stats(
                    Capacity=cpu_capacity,
                    Allocatable=0.0,
                    Requests=Values(
                        InstrumentedValue=0.0,
                        Percent=0.0
                    ),
                    Limits=Values(
                        InstrumentedValue=cpu_commitment,
                        Percent=cpu_commitment_percent
                    )
                ),
                RAM=Stats(
                    Capacity=ram_capacity,
                    Allocatable=0.0,
                    Requests=Values(
                        InstrumentedValue=0.0,
                        Percent=0.0
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



