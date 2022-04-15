from typing import Optional
from fastapi import FastAPI, status
from pykles import logger
from pykles.models import *
from pykles.services import get_probe_status, get_nodes_stats_service


app = FastAPI()


@app.get('/probes', response_model=Ready, description='Endpoint for Kubernetes liveness and readiness probes')
def get_app_status():
    logger.info('REQUEST /probes')
    return get_probe_status()


@app.get('/', response_model=Nodes, description='Retrieve all relevant CPU and RAM stats for all nodes in the cluster')
def default():
    logger.info('REQUEST /')
    return get_nodes_stats_service()

