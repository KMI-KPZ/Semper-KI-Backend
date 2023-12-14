# import time
# from .celery import app
# import logging

# logger = logging.getLogger(__name__)
# # channel_layer = get_channel_layer()

# @app.task
# def dummy_task():
#     logger.info('Executing dummy_task')  # runs on the celery worker
#     time.sleep(10)
#     logger.info('Finished dummy_task')  # runs on the celery worker
#     return print ('The celery task is working!Time taken to run is 10 seconds.')  # will be returned to the backend


# # @app.task
# # def dummy_task(channel_name):
# #     logger.info('Executing dummy_task')  # runs on the celery worker
# #     time.sleep(10)
# #     message = 'task finished in 10 seconds'
# #     logger.info('Finished dummy_task')  # runs on the celery worker
# #     async_to_sync(channel_layer.send)(
# #         channel_name, {"type": "chat.message", "message": message}
# #     )