import traceback
import json
from kubernetes import client, config
from pykles import logger, kubernetes_unit_conversion
import urllib3


def force_decode(string, codecs=['utf8', 'cp1252']):
    # From https://stackoverflow.com/questions/15918314/how-to-detect-string-byte-encoding
    for i in codecs:
        try:
            return string.decode(i)
        except:
            pass
    return string


def get_v1_client():
    try:
        config.load_incluster_config()
        logger.debug('Kubernetes Config Loaded')
        return client.CoreV1Api()
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    raise Exception('Failed to load Kubernetes Config')


def get_api_client():
    try:
        config.load_incluster_config()
        logger.debug('Kubernetes Config Loaded')
        return client.ApiClient()
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    raise Exception('Failed to load Kubernetes Config')


def get_pod_metrics():
    result = None
    try:
        k8s_client = get_api_client()
        (response) = k8s_client.call_api('/apis/metrics.k8s.io/v1beta1/pods', 'GET', response_type='json', _preload_content=False)
        idx = 0
        for item in response:
            logger.debug('response item {} - type(item) = {}'.format(idx, type(item)))
            logger.debug('response item {} - item       = {}'.format(idx, item))
            idx += 1
            if isinstance(item, urllib3.response.HTTPResponse) is True:
                result = json.loads(force_decode(item.data))
                # result = force_decode(item.data)
        logger.debug('type(result)={}'.format(type(result)))
        logger.debug('result={}'.format(result))
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    return result


def get_all_pod_resource_utilization_stats(
    node_id: str,
    next_token: str=None
)->dict:
    cpu_commitment = 0.0
    ram_commitment = 0.0
    cpu_requests = 0.0
    ram_requests = 0.0
    try:
        k8s_client = get_v1_client()
        if next_token is not None:
            response = k8s_client.list_pod_for_all_namespaces(
                field_selector='spec.nodeName={},status.phase!=Failed,status.phase!=Succeeded'.format(node_id),
                limit=100
            )
        else:
            response = k8s_client.list_pod_for_all_namespaces(
                field_selector='spec.nodeName={},status.phase!=Failed,status.phase!=Succeeded'.format(node_id),
                _continue=next_token,
                limit=100
            )
        logger.debug('type(response)={}'.format(type(response)))
        logger.debug('response={}'.format(response))
        logger.debug('_continue={}'.format(response.metadata._continue))
        for pod_data in response.items:                         # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1PodList.md
            pod_metadata = pod_data.metadata                    # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ObjectMeta.md
            pod_spec = pod_data.spec                            # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1PodSpec.md
            pod_status = pod_data.status                        # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1PodStatus.md
            for container_data in pod_spec.containers:          # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Container.md
                container_resources = container_data.resources  # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ResourceRequirements.md
                logger.debug('node_id={}   container_resources={}'.format(node_id, container_resources))
                """
                    NOTE

                        The following link defines the various unit indicators

                        https://kubernetes.io/docs/reference/kubernetes-api/common-definitions/quantity/
                """
                limits = container_resources.limits             # https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
                logger.debug('containerName={}    limits={}'.format(container_data.name, limits))
                if limits is not None:
                    if 'cpu' in limits:
                        cpu_commitment += kubernetes_unit_conversion(value=limits['cpu'])
                    if 'memory' in limits:
                        ram_commitment += kubernetes_unit_conversion(value=limits['memory'])


                requests = container_resources.requests             # https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
                logger.debug('containerName={}    requests={}'.format(container_data.name, requests))
                if requests is not None and limits is not None:
                    if 'cpu' in limits:
                        cpu_requests += kubernetes_unit_conversion(value=requests['cpu'])
                    if 'memory' in limits:
                        ram_requests += kubernetes_unit_conversion(value=requests['memory'])


            
        if response.metadata._continue is not None:
            results = get_all_pod_resource_utilization_stats(
                node_id=node_id,
                next_token=response.metadata._continue
            )
            cpu_commitment += results['CPU']['Limits']
            ram_commitment += results['RAM']['Limits']
            cpu_requests += results['CPU']['Requests']
            ram_requests += results['RAM']['Requests']
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    logger.debug('node={}   cpu={}   ram={}'.format(node_id, cpu_commitment, ram_commitment))
    return {
        'CPU': {
            'Limits': cpu_commitment*1000,
            'Requests': cpu_requests*1000
        },
        'RAM': {
            'Limits': ram_commitment,
            'Requests': ram_requests
        }
    }


def get_nodes(next_token: str=None)->dict:
    nodes = dict()
    try:
        k8s_client = get_v1_client()
        response = None
        if next_token is not None:
            response = k8s_client.list_node(_continue=next_token)
        else:
            response = k8s_client.list_node()   # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#list_node
        logger.debug('type(response)={}'.format(type(response)))
        logger.debug('response={}'.format(response))
        logger.debug('_continue={}'.format(response.metadata._continue))
        for item in response.items:         # ITEM: https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Node.md

            metadata = item.metadata        # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ObjectMeta.md
            spec = item.spec                # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1NodeSpec.md
            status = item.status            # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1NodeStatus.md

            nodes[metadata.name] = dict()
            nodes[metadata.name]['Capacity'] = dict()
            nodes[metadata.name]['Commitments'] = dict()
            nodes[metadata.name]['Requests'] = dict()
            nodes[metadata.name]['Allocatable'] = dict()
            nodes[metadata.name]['Info'] = dict()

            logger.debug('node={}   capacity={}'.format(metadata.name, status.capacity))
            logger.debug('node={}   allocatable={}'.format(metadata.name, status.allocatable))

            nodes[metadata.name]['Capacity'] = dict()
            if 'cpu' in status.capacity:
                nodes[metadata.name]['Capacity']['CPU'] = kubernetes_unit_conversion(value=status.capacity['cpu']) * 1000
            else:
                nodes[metadata.name]['Capacity']['CPU'] = 0.0
            if 'memory' in status.capacity:
                nodes[metadata.name]['Capacity']['RAM'] = kubernetes_unit_conversion(value=status.capacity['memory']) * 1024
            else:
                nodes[metadata.name]['Capacity']['RAM'] = 0.0


            if 'cpu' in status.allocatable:
                nodes[metadata.name]['Allocatable']['CPU'] = kubernetes_unit_conversion(value=status.allocatable['cpu']) * 1000
            else:
                nodes[metadata.name]['Allocatable']['CPU'] = 0.0
            if 'memory' in status.allocatable:
                nodes[metadata.name]['Allocatable']['RAM'] = kubernetes_unit_conversion(value=status.allocatable['memory']) * 1024
            else:
                nodes[metadata.name]['Allocatable']['RAM'] = 0.0


            nodes[metadata.name]['Commitments']['CPU'] = 0.0
            nodes[metadata.name]['Commitments']['RAM'] = 0.0
            nodes[metadata.name]['Requests']['CPU'] = 0.0
            nodes[metadata.name]['Requests']['RAM'] = 0.0
            node_capacity_counters = get_all_pod_resource_utilization_stats(
                node_id=metadata.name
            )
            nodes[metadata.name]['Commitments']['CPU'] = node_capacity_counters['CPU']['Limits']
            nodes[metadata.name]['Commitments']['RAM'] = node_capacity_counters['RAM']['Limits']
            nodes[metadata.name]['Requests']['CPU'] = node_capacity_counters['CPU']['Requests']
            nodes[metadata.name]['Requests']['RAM'] = node_capacity_counters['RAM']['Requests']

        if response.metadata._continue is not None:
            nodes = {**nodes, **get_nodes(next_token=response.metadata._continue)}
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    logger.debug('nodes={}'.format(nodes))
    return nodes


