import redis, os, pickle
from django.conf import settings

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, password=settings.REDIS_PASSWORD)

#######################################################
def addContent(key, content):
    """
    Save a key and its content in redis.

    :param key: key, usually a session ID
    :type key: String
    :param content: The stuff that should be saved
    :type content: Differs, will be set to binary here
    :return: Either "true" if it worked or an error if not
    :rtype: Bool

    """

    try:
        redis_instance.set(key, pickle.dumps(content))
        redis_instance.expire(key, 86400) # 24 hours until deletion of the file
        return True
    except (Exception) as error:
        print(error)
        return error

#######################################################
def deleteKey(key):
    """
    Delete key and value from redis by key.

    :param key: key, usually a session ID
    :type key: String
    :return: Flag to show if it worked or not
    :rtype: Bool

    """
    try:
        redis_instance.delete(key)
    except (Exception) as error:
        print(error)
        return False
    return True

#######################################################
def retrieveContent(key, deleteOrNot=False):
    """
    Retrieve content from redis by key.

    :param key: key, usually a session ID
    :type key: String
    :param deleteOrNot: Decides if the key:content pair should be deleted after retrieval
    :type deleteOrNot: Bool
    :return: content
    :rtype: Differs, not binary

    """
    try:
        retrievedContent = redis_instance.get(key)
        if retrievedContent is not None:
            content = pickle.loads(retrievedContent)
        else:
            return ("", False)
    except (Exception) as error:
        print(error)
        return (error, False)

    if deleteOrNot == True:
        redis_instance.delete(key)

    return (content, True)

