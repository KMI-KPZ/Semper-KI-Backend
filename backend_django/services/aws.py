"""
Part of Semper-KI software

Silvio Weging 2023

Contains: Services for aws cloud storage and file management
"""

import boto3, enum
from io import BytesIO

from django.conf import settings

####################################################################################

class Buckets(enum.StrEnum):
    OTHER = enum.auto() # Everything else
    MODELS = enum.auto() # permanent model files
    FILES = enum.auto() # all uploaded files


class ManageAWS():
    """
    Class for managing access to localstack/local AWS

    """

    #######################################################
    def __init__(self, endpoint, key, secret) -> None:
        """
        Initialize instance with settings for either local or remote storage

        :param endpoint: IP Adress of storage
        :type endpoint: URL Str
        :param key: The access key
        :type key: Str
        :param secret: The secret/password
        :type secret: Str
        """
        self.s3_client = boto3.client("s3", region_name='us-east-1', endpoint_url=endpoint, aws_access_key_id=key, aws_secret_access_key=secret)
        #TODO: avoid this if they've already been created in localstack, avoid this at all costs in AWS
        self.createBucket("other")
        self.createBucket("models")
        self.createBucket("files")

    #######################################################
    def createBucket(self, bucketName):
        """
        Create a named bucket to put stuff in.

        :param bucketName: Name of the bucket
        :type bucketName: Str
        :return: Success or error
        :rtype: Bool or Error
        """
        response = self.s3_client.create_bucket(ACL='private',Bucket=bucketName)
        # TODO if response...

        return True


    #######################################################
    def uploadFile(self, bucketName, fileKey, file):
        """
        Upload a binary in-memory file to storage.

        :param bucketName: Name of the bucket
        :type bucketName: Str
        :param fileKey: The key with which to retrieve the file again later
        :type fileKey: Str
        :param file: InMemory BytesIO object containing a file
        :type file: BytesIO InMemoryFile
        :return: Success or error
        :rtype: Bool or Error
        """

        file.file.seek(0) # because read() is called and has to start at the front of the file
        response = self.s3_client.upload_fileobj(file.file, bucketName, fileKey)
        # TODO if response...

        return True

    #######################################################
    def downloadFile(self, bucketName, fileKey):
        """
        Upload a binary in-memory file to storage.

        :param bucketName: Name of the bucket
        :type bucketName: Str
        :param fileKey: The key with which to retrieve the file again later
        :type fileKey: Str
        :return: File or error
        :rtype: BytesIO or Error
        """

        output = BytesIO()
        fileObj = self.s3_client.download_fileobj(bucketName, fileKey, output)
        output.seek(0)
        if output.getbuffer().nbytes == 0: # is empty so no file has been downloaded
            return (output, False)
        return (output, True)
    
    #######################################################
    def deleteFile(self, bucketName, fileKey):
        """
        Delete a file from storage.

        :param bucketName: Name of the bucket
        :type bucketName: Str
        :param fileKey: The key with which to retrieve the file again later
        :type fileKey: Str
        :return: File or error
        :rtype: BytesIO or Error
        """

        response = self.s3_client.delete_object(Bucket=bucketName, Key=fileKey)
        # TODO: if response...

        return True

manageLocalAWS = ManageAWS(settings.LOCALSTACK_ENDPOINT, settings.LOCALSTACK_ACCESS_KEY, settings.LOCALSTACK_SECRET)
manageRemoteAWS = ManageAWS(settings.AWS_ENDPOINT, settings.AWS_ACCESS_KEY, settings.AWS_SECRET)