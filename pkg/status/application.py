import time
import logging
from pkg.utils.annotation.annotation import IsPodParentAnnotated
logging.basicConfig(format='time=%(asctime)s level=%(levelname)s  msg=%(message)s', level=logging.INFO)  

class Application(object):
	def __init__(self, appNs=None, appLabel=None, containerName=None, timeout=None, delay=None, clients=None, chaosDetails=None, 
	AuxiliaryAppDetails=None, states=None, duration=None, podName=None , ContainerStatuses=None):
		self.appNs                   = appNs
		self.appLabel                = appLabel
		self.containerName           = containerName
		self.timeout                 = timeout
		self.chaosDetails            = chaosDetails
		self.delay                   = delay
		self.clients                 = clients
		self.states                  = states
		self.AuxiliaryAppDetails     = AuxiliaryAppDetails
		self.duration                = duration             
		self.podName                 = podName
		self.ContainerStatuses       = ContainerStatuses


	# AUTStatusCheck checks the status of application under test
	# if annotationCheck is true, it will check the status of the annotated pod only
	# else it will check status of all pods with matching label
	def AUTStatusCheck(self, appNs, appLabel, containerName, timeout, delay, chaosDetails, clients):
		self.timeout = timeout
		self.delay = delay
		if chaosDetails.AppDetail.AnnotationCheck == True:
			logging.info("Check Annotated for Applications Status")
			return self.AnnotatedApplicationsStatusCheck(clients, appNs, appLabel, containerName, chaosDetails, 0)
		else:
			if appLabel == "" :
				# Checking whether applications are healthy
				logging.info("[status]: No appLabels provided, skipping the application status checks")
			else:
				# Checking whether application containers are in ready state
				logging.info("[status]: Checking whether application containers are in ready state")
				self.CheckContainerStatus(clients, appNs, appLabel, containerName, 0)
				
				# Checking whether application pods are in running state
				logging.info("[status]: Checking whether application pods are in running state")
				err = self.CheckPodStatus(clients, appNs, appLabel, 0)
				if err != None:
					return err
		return None
	

	#AnnotatedApplicationsStatusCheck checks the status of all the annotated applications with matching label
	def AnnotatedApplicationsStatusCheck(self, clients, appNs, appLabel, containerName, chaosDetails, init):
		try:
			time.sleep(self.delay)
			if init < self.timeout:
				podList = clients.clientCoreV1.list_namespaced_pod(appNs, label_selector=appLabel)
				if len(podList.items) == 0:
					raise Exception("Unable to find the pods with matching labels")
				for pod in podList.items:
					isPodAnnotated, err = IsPodParentAnnotated(pod, chaosDetails, clients)
					if err != None:
						raise Exception(err)
					if isPodAnnotated == True:
						if containerName == "":
							for  container in pod.status.container_statuses:
								if container.state.terminated != None: 
									raise Exception("Container is in terminated state")
								
								if container.ready == False:
									raise Exception("containers are not yet in running state")
								
								logging.info("[status]: The Container status are as follows Container : %s, Pod : %s, Readiness : %s", container.name, pod.metadata.name, container.ready)
							
						else:
							for container in pod.status.container_statuses:
								if containerName == container.name:
									if container.state.terminated != None:
										raise Exception("container is in terminated state")
									
									if container.ready == False:
										raise Exception("containers are not yet in running state")
									
									logging.info("[status]: The Container status are as follows Container : %s, Pod : %s, Readiness : %s.", container.name, pod.metadata.name, container.ready)
						if pod.status.phase != "Running":
							raise Exception("%s pod is not yet in running state", pod.metadata.name)
						
						logging.info("[status]: The status of Pods are as follows Pod : %s, status : %s.", pod.metadata.name, pod.status.phase)
			else:
				return logging.error("Unable to find containers are in running state, timeout")	
		except Exception as e:
			if(e != None):
				self.AnnotatedApplicationsStatusCheck(clients,appNs, appLabel, containerName, chaosDetails, init = init + self.delay)
				
		return None

	# CheckApplicationStatus checks the status of the AUT
	def CheckApplicationStatus(self, appNs, appLabel, timeout, delay, clients):
		
		self.timeout = timeout
		self.delay = delay
		if appLabel == "":
			# Checking whether applications are healthy
			logging.warning("[status]: No appLabels provided, skipping the application status checks")
		else:
			# Checking whether application containers are in ready state
			logging.info("[status]: Checking whether application containers are in ready state")
			err = self.CheckContainerStatus(clients,appNs, appLabel, "", 0)
			if err != None:
				return err
			
			# Checking whether application pods are in running state
			logging.info("[status]: Checking whether application pods are in running state")
			err = self.CheckPodStatus(clients, appNs, appLabel, 0); 
			if err != None:
				return err

		return None
	

	# CheckAuxiliaryApplicationStatus checks the status of the Auxiliary applications
	def CheckAuxiliaryApplicationStatus(self, AuxiliaryAppDetails, timeout, delay):

		AuxiliaryAppInfo = AuxiliaryAppDetails.split(",")
		self.timeout = timeout
		self.delay = delay
		for val in AuxiliaryAppInfo:
			AppInfo = val.split(":")
			err = self.CheckApplicationStatus(AppInfo[0], AppInfo[1])
			if err != None:
				return err

		return None
	
	# CheckPodStatusPhase is helper to checks the running status of the application pod
	def CheckPodStatusPhase(self,clients, appNs, appLabel, states, init):
		
		try:
			time.sleep(self.delay)
			if init < self.timeout:
				podList = clients.clientCoreV1.list_namespaced_pod(appNs, label_selector=appLabel)
				for pod in podList.items:
					if str(pod.status.phase) != states: 
						raise Exception("Pod is not yet in %s state(s)",(states))
				
					logging.info("[status]: The status of Pods are as follows Pod : %s status : %s", pod.metadata.name, pod.status.phase)
			else:
				return logging.error("Pod are not yet in running state(s)")
		except Exception as e:
			if(e != None):
				self.CheckPodStatusPhase(clients, appNs,appLabel, states, init = init + self.delay)
				
		return None

	# CheckPodStatus checks the running status of the application pod
	def CheckPodStatus(self, clients, appNs, appLabel, tries):
		return self.CheckPodStatusPhase(clients, appNs, appLabel, "Running", tries)
	
	#CheckContainerStatus checks the status of the application container for given timeout, if it does not match label it will 
	def CheckContainerStatus(self, clients, appNs, appLabel, containerName, init):
		
		try:
			time.sleep(self.delay)
			if init < self.timeout:
				podList = clients.clientCoreV1.list_namespaced_pod(appNs, label_selector=appLabel)
				
				if len(podList.items) == 0:
					raise Exception("Unable to find the pods with matching labels")
				for pod in podList.items:
					if containerName == "":
						err = self.validateAllContainerStatus(pod.metadata.name, pod.status.container_statuses, clients)
						if err != None:
							raise Exception(err)
					else:
						err = self.validateContainerStatus(containerName, pod.metadata.name, pod.status.container_statuses, clients); 
						if err != None:
							raise Exception(err)
			else:
				return logging.error("Unable to find the pods with matching labels, timeout")
		except Exception as e:
			if(e != None):
				self.CheckContainerStatus(clients, appNs,appLabel,containerName,  init = init + self.delay)
				
		return None


	# validateContainerStatus verify that the provided container should be in ready state
	def validateContainerStatus(self, containerName, podName, ContainerStatuses, clients):
		for container in ContainerStatuses:
			if container.name == containerName:
				if container.state.terminated != None :
					return logging.warning("container is in terminated state")
				
				if container.ready == False :
					return logging.warning("containers are not yet in running state")
				
				logging.info("[status]: The Container status are as follows Container : %s, Pod : %s, Readiness : %s", container.name, podName, container.ready)
		return None
	

	# validateAllContainerStatus verify that the all the containers should be in ready state
	def validateAllContainerStatus(self, podName, ContainerStatuses, clients):
		for container in ContainerStatuses:
			err = self.validateContainerStatus(container.name, podName, ContainerStatuses, clients)
			if err != None:
				return logging.error(err)
		return None
	
	# WaitForCompletionPhase wait until the completion of pod
	def WaitForCompletionPhase(self, clients, appNs, appLabel, duration, containerName, init):
		podStatus = ''
		failedPods = 0
		self.duration = duration
		# It will wait till the completion of target container
		# it will retries until the target container completed or met the timeout(chaos duration)
		try:
			time.sleep(self.delay)
			if init < self.timeout:
			
				try:
					podList = clients.clientCoreV1.list_namespaced_pod(appNs, label_selector=appLabel)
				except Exception as e:
					return e
				# it will check for the status of helper pod, if it is Succeeded and target container is completed then it will marked it as completed and return
				# if it is still running then it will check for the target container, as we can have multiple container inside helper pod (istio)
				# if the target container is in completed state(ready flag is false), then we will marked the helper pod as completed
				# we will retry till it met the timeout(chaos duration)
				failedPods = 0
				for pod in podList.items :
					podStatus = str(pod.status.phase)
					logging.info("Helper pod status: %s",(podStatus))
					if podStatus != "Succeeded" & podStatus != "Failed":
						for container in pod.status.container_statuses:
							if container.name == containerName and container.ready:
								return logging.error("Container is not completed yet")
					
					if podStatus == "Pending" :
						return logging.warning("pod is in pending state")
					
					logging.info("[status]: The running status of Pods are as follows Pod : %s status : %s", pod.metadata.name, podStatus)
					if podStatus == "Failed":
						failedPods = failedPods + 1
			else:
				return logging.error("Unable to find the container in running state, timeout")
		except Exception as err:
			self.WaitForCompletionPhase(clients, appNs, appLabel, duration, containerName, init = init + self.delay)
		if failedPods > 0:
			return "Failed", logging.warning("pod is in pending state")	
		return podStatus, None

	# WaitForCompletion wait until the completion of pod
	def WaitForCompletion(self, appNs, appLabel, duration, containerName, clients):

		return self.WaitForCompletionPhase(appNs, clients, appLabel, duration, containerName, 0)

	# CheckHelperStatusPhase checks the status of the helper pod
	# and wait until the helper pod comes to one of the {running,completed} states
	def CheckHelperStatusPhase(self, clients, appNs, appLabel, init):
		try:
			time.sleep(self.delay)
			if init < self.timeout:
				try:
					podList = clients.clientCoreV1.list_namespaced_pod(appNs, label_selector=appLabel)
				except Exception as e:
					return e
				for  pod in podList.items:
					podStatus = str(pod.status.phase)
					if podStatus.lower() == "running" or podStatus.lower() == "succeeded":
						logging.info("%s helper pod is in %s state",(pod.metadata.name, podStatus))
					else:
						return logging.warning("%s pod is in %s state",(pod.metadata.name, podStatus))
					
					for container in pod.status.container_statuses:
						if container.state.terminated & pod.status.phase != "Completed" :
							return logging.info("container is terminated with %s reason",(pod.status.reason))
			else:
				return logging.error("Unable to find the Helper pod in running state, timeout") 
		except Exception as e:
			self.CheckHelperStatusPhase(clients, appNs, appLabel, init = init + self.delay)	
		return None

	# CheckHelperStatus checks the status of the helper pod
	# and wait until the helper pod comes to one of the {running,completed} states
	def CheckHelperStatus(self, appNs, appLabel, timeout, delay, clients):
		self.timeout = timeout
		self.delay = delay
		return self.CheckHelperStatusPhase(clients, appNs, appLabel)
