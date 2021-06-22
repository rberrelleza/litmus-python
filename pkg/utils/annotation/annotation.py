
import logging

# deployment derive the deployment details belongs to the given labels
# it extract the parent name from the owner references
def deployment(targetPod,chaosDetails, clients):
	deployList = clients.clientApps.list_namespaced_deployment(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	if len(deployList.items) == 0:
		return False, ValueError("no deployment found with matching label")

	for deploy in deployList.items:
		if str(deploy.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			rsOwnerRef = targetPod.metadata.owner_references
			for own in rsOwnerRef :
				if own.kind == "ReplicaSet" :
					try:
						rs = clients.clientApps.read_namespaced_replica_set(own.name, chaosDetails.AppDetail.Namespace)
					except Exception as e:
						return False, e
					ownerRef = rs.metadata.owner_references
					for own in ownerRef:
						if own.kind == "Deployment" and own.name == deploy.metadata.name:
							logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",chaosDetails.AppDetail.Kind, deploy.metadata.name, deploy.metadata.namespace)
							return True, None
	return False, False

# statefulset derive the statefulset details belongs to the given target pod
# it extract the parent name from the owner references
def statefulset(targetPod,chaosDetails, clients):
	
	stsList = clients.clientApps.list_namespaced_stateful_set("litmus")
	if len(stsList.items) == 0:
		return False, ValueError("no statefulset found with matching label")

	for sts in stsList.items:
		if str(sts.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			ownerRef = targetPod.metadata.owner_references
			for own in ownerRef:
				if own.kind == "StatefulSet" and own.name == sts.name:
					logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",chaosDetails.AppDetail.Kind, sts.metadata.name, sts.metadata.namespace)
					return True, None

# daemonset derive the daemonset details belongs to the given target pod
# it extract the parent name from the owner references
def daemonset(targetPod, chaosDetails, clients):
	
	dsList = clients.clientApps.list_namespaced_daemon_set(chaosDetails.AppDetail.Namespace, label_selector=chaosDetails.AppDetail.Label)
	if len(dsList.items) == 0:
		return False, ValueError("no daemonset found with matching label")
	
	for ds in dsList.items:
		if str(ds.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			ownerRef = targetPod.metadata.owner_references
			for own in ownerRef:
				if own.kind == "DaemonSet" and own.name == ds.name:
					logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",chaosDetails.AppDetail.Kind, ds.metadata.name, ds.metadata.namespace)
					return True, None

# deploymentConfig derive the deploymentConfig details belongs to the given target pod
# it extract the parent name from the owner references
def deploymentConfig(targetPod, chaosDetails, clients):

	try:
		deploymentConfigList = clients.clientDyn.resources.get(api_version="v1", kind="DeploymentConfig", group="apps.openshift.io", label_selector=chaosDetails.AppDetail.Label)
	except Exception as e:
		return False, e
	if len(deploymentConfigList.items) == 0:
		return False, ValueError("no deploymentconfig found with matching labels")
	
	for dc in deploymentConfigList.items:
		if str(dc.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			rcOwnerRef = targetPod.metadata.owner_references
			for own in range(rcOwnerRef):
				if own.kind == "ReplicationController":
					try:
						rc = clients.clientCoreV1.read_namespaced_replication_controller(own.name, chaosDetails.AppDetail.Namespace)
					except Exception as e:
						return False, e
					
					ownerRef = rc.metadata.owner_references
					for own in ownerRef:
						if own.kind == "DeploymentConfig" and own.name == dc.GetName():
							logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",chaosDetails.AppDetail.Kind, dc.metadata.name, dc.metadata.namespace)
							return True, None

# rollout derive the rollout details belongs to the given target pod
# it extract the parent name from the owner references
def rollout(targetPod, chaosDetails, clients):
	
	try:
		rolloutList = clients.clientDyn.resources.get(api_version="v1alpha1", kind="Rollout", group="argoproj.io", label_selector=chaosDetails.AppDetail.Label)
	except Exception as e:
		return False, e
	if len(rolloutList.items) == 0:
		return False, ValueError("no rolloutList found with matching labels")
	for ro in rolloutList.items :
		if str(ro.metadata.annotations.get(chaosDetails.AppDetail.AnnotationKey) != None) == str((chaosDetails.AppDetail.AnnotationValue == 'true')):
			rsOwnerRef = targetPod.metadata.owner_references
			for own in rsOwnerRef :
				if own.kind == "ReplicaSet":
					try:
						rs = clients.clientsAppsV1.read_namespaced_replica_set(own.name, chaosDetails.AppDetail.Namespace)
					except Exception as e:
						return False, e
					
					ownerRef = rs.metadata.owner_references
					for own in ownerRef:
						if own.kind == "Rollout" and own.name == ro.metadata.name:
							logging.info("[Info]: chaos candidate of kind: %s, name: %s, namespace: %s",chaosDetails.AppDetail.Kind, ro.metadata.name, ro.metadata.namespace)
							return True, None

# PodParentAnnotated is helper method to check whether the target pod's parent is annotated or not
def PodParentAnnotated(argument, targetPod, chaosDetails, clients):
	
	if argument == "deployment":
		return deployment(targetPod,chaosDetails, clients)
	elif argument == "statefulset": 
		return statefulset(targetPod,chaosDetails, clients)
	elif argument == "daemonset": 
		return daemonset(targetPod,chaosDetails, clients)
	elif argument == "deploymentConfig": 
		return deploymentConfig(targetPod,chaosDetails, clients)
	elif argument == "rollout" : 
		return rollout(targetPod,chaosDetails, clients)
	else:
		return False,  logging.info("Appkind: %s is not supported",(argument))
	
# IsPodParentAnnotated check whether the target pod's parent is annotated or not
def IsPodParentAnnotated(targetPod, chaosDetails, clients):
	return PodParentAnnotated(chaosDetails.AppDetail.Kind.lower(), targetPod,chaosDetails, clients)
