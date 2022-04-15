import traceback
from kubernetes import client, config
from pykles import logger, kubernetes_unit_conversion


def get_v1_client():
    try:
        config.load_incluster_config()
        logger.debug('Kubernetes Config Loaded')
        return client.CoreV1Api()
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    raise Exception('Failed to load Kubernetes Config')


def get_all_pod_resource_utilization_stats(
    node_id: str,
    next_token: str=None
)->dict:
    cpu_commitment = 0.0
    ram_commitment = 0.0
    try:
        client = get_v1_client()
        if next_token is not None:
            response = client.list_pod_for_all_namespaces(
                field_selector='spec.nodeName={},status.phase!=Failed,status.phase!=Succeeded'.format(node_id),
                limit=100
            )
        else:
            response = client.list_pod_for_all_namespaces(
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

                        Here we are only interested in the LIMITS as this is an indicator for the maximum resources 
                        required for the pod. In order to observe the node capacity, this is the only numner to really 
                        worry about, since we expect that all deployed resources will be used for testing, and given 
                        the nature of the applications, it can be assumed that the maximum resource commitments are 
                        achievable.

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
        if response.metadata._continue is not None:
            results = get_all_pod_resource_utilization_stats(
                node_id=node_id,
                next_token=response.metadata._continue
            )
            cpu_commitment += results['CPU']
            ram_commitment += results['RAM']
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    logger.debug('node={}   cpu={}   ram={}'.format(node_id, cpu_commitment, ram_commitment))
    return {
        'CPU': cpu_commitment*1000,
        'RAM': ram_commitment
    }


def get_nodes(next_token: str=None)->dict:
    nodes = dict()
    try:
        client = get_v1_client()
        response = None
        if next_token is not None:
            pass
        else:
            response = client.list_node()
        logger.debug('type(response)={}'.format(type(response)))
        logger.debug('response={}'.format(response))
        logger.debug('_continue={}'.format(response.metadata._continue))
        for item in response.items:     # ITEM: https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Node.md
            metadata = item.metadata    # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ObjectMeta.md
            spec = item.spec            # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1NodeSpec.md
            status = item.status        # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1NodeStatus.md
            nodes[metadata.name] = dict()
            nodes[metadata.name]['Labels'] = metadata.labels
            nodes[metadata.name]['Info'] = dict()
            logger.debug('node={}   capacity={}'.format(metadata.name, status.capacity))
            nodes[metadata.name]['Capacity'] = dict()
            if 'cpu' in status.capacity:
                nodes[metadata.name]['Capacity']['CPU'] = kubernetes_unit_conversion(value=status.capacity['cpu']) * 1000
            else:
                nodes[metadata.name]['Capacity']['CPU'] = 0.0
            if 'memory' in status.capacity:
                nodes[metadata.name]['Capacity']['RAM'] = kubernetes_unit_conversion(value=status.capacity['memory']) * 1024
            else:
                nodes[metadata.name]['Capacity']['RAM'] = 0.0
            nodes[metadata.name]['Commitments'] = dict()
            nodes[metadata.name]['Commitments']['CPU'] = None
            nodes[metadata.name]['Commitments']['RAM'] = None
            node_capacity_commitments = get_all_pod_resource_utilization_stats(
                node_id=metadata.name
            )
            nodes[metadata.name]['Commitments']['CPU'] = node_capacity_commitments['CPU']
            nodes[metadata.name]['Commitments']['RAM'] = node_capacity_commitments['RAM']
        if response.metadata._continue is not None:
            nodes = {**nodes, **get_nodes(next_token=response.metadata._continue)}
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    logger.debug('nodes={}'.format(nodes))
    return nodes


