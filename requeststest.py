"""
Part of Semper-KI software

Akshay NS 2023

Contains: Handlers for interacting with Celery tasks using Flower API

"""

###################################################################

import requests

import time

#####################################################################

class CeleryTaskManager:
    def __init__(self, taskname, data):
        self.taskname = taskname
        self.data = data
        self.task_id = None
        
        self.session = requests.Session()
        self.base_url = 'http://flower:8888/api'

        # Start the task and get the task ID
        self.start_task()

    def start_task(self):
        """
        Start a celery task
        :param request: POST Request
        :type request: HTTP POST
        :return: JSON Response with task-id of the task that is started
        :rtype: JSON Response
        
        """
        url = f'{self.base_url}/task/send-task/{self.taskname}'
        response = self.session.post(url, json=self.data)

        if response.status_code == 200:
            self.task_id = response.json().get('task-id')
            print(f'Task {self.taskname} started successfully with task ID: {self.task_id}')
        else:
            print(f'Failed to start the task {self.taskname}. Status code: {response.status_code}')


    def gettaskid(self):
        return self.task_id        

    def check_status(self):
        """
        Check the status of a celery task
        :param request: GET Request
        :type request: HTTP GET
        :return: JSON Response with metadata (taskid, status) of the task that is started
        :rtype: JSON Response
        
        """
        if self.task_id is not None:
            url = f'{self.base_url}/task/info/{self.task_id}'
            
            while True:
                response = self.session.get(url)
                
                if response.status_code == 200:
                    task_info = response.json()
                    state = task_info.get('state')
                    if state == 'SUCCESS':
                        result = task_info.get('result')
                        print(f'Task {self.taskname} is completed. Result: {result}')
                        return result 
                 
                    elif state == 'PENDING':
                        eta = task_info.get('eta')
                        print(f'Task {self.taskname} is still pending. ETA: {eta}')
                        return eta
                    else:
                        pass
                        # print(f'Task {self.taskname} is in state: {state}')
                else:
                    print(f'Failed to get task status. Status code: {response.status_code}')
                
                time.sleep(1)  # Wait for 1 second before checking the status again
        else:
            print('Task ID is not available. Make sure the task is started.')


########################################################################################
# 1. send tasks with arguments
#     and obtain the taskid
# 2. get the status of the task from the taskid
# 3. show the results of the task from the taskid.

# APIs to communicate with flower to perform the above tasks
# https://flower.readthedocs.io/en/latest/api.html
#POST http://flower:8888/api/task/send-task/taskname
#GET  http://flower:8888/api/task/result/taskid
   
# Example usage
# data = {
#     "args": [4, 77]
# }
# task_manager = CeleryTaskManager(taskname='trialtask', data=data)
# task_manager.check_status()









