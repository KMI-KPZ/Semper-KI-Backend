# from time import sleep
# import requests
# session = requests.Session()
# # r = requests.get('http://localhost:8888/api/workers')
# # r.textr
# # # print(r.text)
# data = {
#     "args": [2, 7 ]
# }
# # url = 'http://localhost:8888/api/task/send-task/trialtask'
# y = requests.post(url, json=data)
# sleep(5)
# taskid = y.json().get('task-id')
# print(taskid)
# url2 = 'http://localhost:8888/api/task/result/'+taskid

# t = requests.get(url2)
# finalresult = t.json().get('result')
# print(finalresult)


###################################################################
# 1. send tasks with arguments
#     and obtain the taskid
# 2. get the status of the task from the taskid
# 3. show the results of the task from the taskid.

# APIs to communicate with flower to perform the above tasks
# https://flower.readthedocs.io/en/latest/api.html
#POST http://flower:8888/api/task/send-task/taskname
#GET  http://flower:8888/api/task/result/taskid
 
# def sendtask(taskname, data):
#     url = f'http://localhost:8888/api/task/send-task/{taskname}'
#     post_task = session.post(url, json=data)
#      # Check if the request was successful before extracting the task ID
#     try:
#         taskid = post_task.json().get('task-id')  # Use 'task-id' key to get the task ID
#         taskinfo = session.get(f'http://localhost:8888/api/task/info/{taskid}')
#         return print(taskinfo.json().get('state'))
#         # return print(f'The task: {taskname} :was started successfully with task-id:{taskid}')
#     except post_task.status_code != 200:
#         return print(f'failed to start the task: {taskname}')
#         # return print(f'Failed to start the task {taskname}. Status code: {post_task.status_code}')

# sendtask(taskname='trialtask', data=data)

import requests
import time

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
                        
                       
                        
                        break  # Exit the loop when the task is completed
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

    

# Example usage
data = {
    "args": [4, 77]
}

# Specify the callback URL when creating the CeleryTaskManager instance

# task_manager = CeleryTaskManager(taskname='trialtask', data=data)
# task_manager.check_status()









