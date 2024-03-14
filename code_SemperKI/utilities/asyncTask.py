"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Send away a task in a fire-and-forget fashion
"""

import asyncio, inspect
from asgiref.sync import sync_to_async

####################################################################
async def doTask(task, params:tuple=None):
    """
    Send some task with params to an async computation in a fire-and-forget kinda way.

    :param task: The task at hand
    :type task: Function object
    :param params: The parameters of the function, can be None if there aren't any
    :type params: tuple or None
    :return: Nothing, it's fire and forget, you know
    :rtype: None
    """
    if inspect.iscoroutinefunction(task):
        if params == None:
            nothing = await task()
        else:
            nothing = await task(*params)
    else:
        if params == None:
            nothing = await sync_to_async(task)()
        else:
            nothing = await sync_to_async(task)(*params)

    return

####################################################################
def run(task, params:tuple=None):
    """
    Call this from any sync function.

    :param task: The task at hand
    :type task: Function object
    :param params: The parameters of the function, can be None if there aren't any
    :type params: tuple or None
    :return: Nothing, it's fire and forget, you know
    :rtype: None
    """

    asyncio.run(doTask(task, params))

    return 
