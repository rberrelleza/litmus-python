#!/usr/bin/env python3

import experimentList.generic.podDelete.podDelete as podDelete
import argparse
import os
import logging
from pkg.utils.client.client import Configuration, K8sClient

logging.basicConfig(format='time=%(asctime)s level=%(levelname)s  msg=%(message)s', level=logging.INFO)  
def main():
	parser = argparse.ArgumentParser()
	
	# parse the experiment name
	parser.add_argument("-experimentName", action='store',
                    default="pod-delete",
                    dest="experimentName",
                    help="Chaos experiment to chose for execution"
                    )
	parser.add_argument("-kubeContext",
                    required=False,
                    default=os.environ.get("KUBECONFIG", ""),
                    dest='kubeContext',
                    help="Kubernetes client ignore SSL")
	args = parser.parse_args()
	
	config = Configuration(kubeContext=args.kubeContext)
	clients = K8sClient(conf = config.get_config())
	logging.info("Experiment Name: {}".format(args.experimentName))

	# invoke the corresponding experiment based on the the (-name) flag
	if args.experimentName == "pod-delete":
		podDelete.PodDelete(clients)
	else:
		logging.warning("Unsupported -name {}, please provide the correct value of -name args".format(args.experimentName))
	return
if __name__ == "__main__":
	main()
	