from kubernetes import client, config
from kubernetes import dynamic
from kubernetes.client import api_client
# Configs can be set in Configuration class directly or using helper utility

# print(con)
# v1 = client.CoreV1Api()
# print("Listing pods with their IPs:")

import os
from kubernetes.client.api import core_v1_api

from kubernetes.client.configuration import Configuration
from kubernetes.config import kube_config
#from openshift.dynamic import DynamicClient



# DEFAULT_E2E_HOST = '127.0.0.1'
# configura = client.Configuration()
# configura.debug = True
# configura.host = "http://127.0.0.1:8443"
# configura.verify_ssl = False
# configura.proxy = None
# configs = config.load_incluster_config(client_configuration = configura)
# print(configs, configura)
# def get_e2e_configuration():
#     confi = Configuration()
#     confi.host = 'https://127.0.0.1:8443'
#     confi.verify_ssl = False
#     confi.assert_hostname = False
#     configs = config.load_incluster_config(client_configuration = confi)
    # if os.path.exists(os.path.expanduser(kube_config.KUBE_CONFIG_DEFAULT_LOCATION)) == True:
    #     kube_config.load_kube_config(client_configuration=config)
    # else:
    #     print('Unable to load config from %s' %
    #           kube_config.KUBE_CONFIG_DEFAULT_LOCATION)
    #     for url in ['https://%s:8443' % DEFAULT_E2E_HOST,
    #                 'http://%s:8080' % DEFAULT_E2E_HOST]:
    #         try:
    #             urllib3.PoolManager().request('GET', url)
    #             config.host = url
    #             config.verify_ssl = False
    #             urllib3.disable_warnings()
    #             break
    #         except urllib3.exceptions.HTTPError:
    #             pass
    # if config.host is None:
    #     raise unittest.SkipTest('Unable to find a running Kubernetes instance')
    # print('Running test against : %s' % configs)
    # return configs
global conf
if os.getenv('KUBERNETES_SERVICE_HOST'):
    conf = config.load_incluster_config()
else:
    conf = config.load_kube_config()
v1=client.CoreV1Api()
# List = []
# try:
#     print("start")
#     resp = v1.list_namespaced_pod(namespace='ss')
#     print((resp))
# except:
#     return logging.error("Failed to create event with err: %s", exp)
# 	print("Done")
# c = 0
# for pod in resp.items:
#     List.append(pod)
# li = client.V1PodList
# li = client.V1PodList(items=List)
# print(len(li.items))
# podNames = []
# for pod in li.items:
#     podNames.append(str(pod.metadata.name))
# print(podNames)
# print(li.items[0].metadata.name)
clientDyn = dynamic.DynamicClient(api_client.ApiClient(conf))
# print(clientDyn, conf)

# podNames = []
# for pod in li.items:
#     print("name ;", pod.metadata.name)
#     podNames.append(pod.metadata.name)
# print(podNames)
# k8s_client = config.new_client_from_config()
# dyn_client = DynamicClient(k8s_client)


print("start2")
chaosResults = clientDyn.resources.get(api_version="litmuschaos.io/v1alpha1", kind="ChaosResult").get()
print(chaosResults.items[0].metadata.name)
print("Done2")

# print("start2")
# chaosResults = clientDyn.resources.get(api_version="litmuschaos.io/v1alpha1", kind="ChaosResult").get()
# print(len(chaosResults.items))

# print("Done2")
