import base64
from logging import getLogger

import psutil
from boto3.s3.transfer import TransferConfig
from django.core.management.base import BaseCommand
from Generic_Backend.code_General.connections.s3 import manageRemoteS3, manageLocalS3
from Generic_Backend.code_General.utilities.crypto import EncryptionAdapter
from code_SemperKI.handlers.public.files import moveFileToRemote

logging = getLogger("django_debug")


####################################################################################
class Command(BaseCommand):
    """
    Loads a file from disk sends it unencrypted to local stack/minio
    then loads it encrypted to AWS S3 compatible storage and then loads it back meanwhile decrypting it
    and printing out memory consumption and comparing the files
    later it uses the moveFileToRemote method to move the file from local stack to remote storage and tests it again
    should function as a memory consumption and functionality test
    the goal is to only have a certain amount of memory used like 5MB (x parts used) for the transfer

    """
    help = 'sends a test mail to see if config is correct'
    debugLogger = logging

    ##############################################
    def add_arguments(self, parser):
        """

        :param parser: command line parser
        :type parser: ArgumentParser
        :return: None
        :rtype: None
        """

        #file to load
        parser.add_argument('file', type=str, help='the file to load')
        #optional: amount of concurrent parts for the multipart upload
        parser.add_argument('--concurrency', type=int, help='the amount of concurrent parts for the multipart upload', default=1)
        #do not delete in the end
        parser.add_argument('--keep', action='store_true', help='do not delete the file in the end')
        #chunksize for decrypt reading file
        parser.add_argument('--chunksize', type=int, help='the chunksize for reading the file from remote storage', default=5*1024*1024)

    ##############################################

    def handle(self, *args, **options):
        """
        :param self: Command object
        :type self: Command
        :param args: arguments
        :type args: list
        :param options: options
        :type options: dict
        :return: None
        :rtype: None
        """

        file_path = options['file']
        concurrency = options['concurrency']
        keep = options['keep']
        self._logMemInfo("launching")
        fileKey = "buffertest_"+file_path
        chunksize = options['chunksize']


        file = open(file_path, 'rb')
        fileKeyEnc = fileKey + ".enc"

        encryptionAdapterToLocalStack = EncryptionAdapter(file).setDebugLogger(self.debugLogger)
        config = TransferConfig(
            multipart_threshold=1024 * 1024 * 5,  # Upload files larger than 5 MB in multiple parts (default: 8 MB)
            max_concurrency= concurrency,  # Use 10 threads for large files (default: 10, max 10)
            multipart_chunksize=1024 * 1024 * 5,  # 5 MB parts (min / default: 5 MB)
            use_threads=True  # allow threads for multipart upload
        )

        print(f'###############################\nuploading file to local stack with concurrent {concurrency} parts\n###############################')
        manageLocalS3.uploadFileObject(fileKey, encryptionAdapterToLocalStack, config)

        streamingBodyLocal, flag = manageLocalS3.getFileStreamingBody(fileKey)
        if not streamingBodyLocal:
            print("Error while accessing stream object")
            return


        print(f'###############################\nuploading file to remote storage with concurrent {concurrency} parts\n###############################')
        encryptionAdapterToAWS = EncryptionAdapter(streamingBodyLocal).setDebugLogger(self.debugLogger)
        # encrypts that what will be read from the source - managing the encryption key/Iv
        encryptionAdapterToAWS.setupEncryptOnRead(base64.b64decode(manageRemoteS3.aesEncryptionKey))

        # upload the encrypted file to the remote storage
        manageRemoteS3.uploadFileObject(fileKeyEnc, encryptionAdapterToAWS, config)

        # Monitor memory usage
        encryptionAdapterToAWS = None # free memory


        # Download the file from S3 and monitor memory usage
        streamingBody, flag = manageRemoteS3.getFileStreamingBody(fileKeyEnc)

        if not flag:
            print("Error while downloading file")
            return

        decryptionAdapter = EncryptionAdapter(streamingBody)
        decryptionAdapter.debugLogger = self.debugLogger
        decryptionAdapter.setupDecryptOnRead(base64.b64decode(manageRemoteS3.aesEncryptionKey))

        print(f'###############################\ncomparing files\n###############################')
        self.compareFiles(file_path, decryptionAdapter, chunksize)
        print(f'###############################\nfirst try completed\n###############################')

        # delete remote file before sending it with internal move method
        manageRemoteS3.deleteFile(fileKeyEnc)
        print(f'###############################\nmoving file with internal method\n###############################')
        moveFileToRemote(fileKey, fileKeyEnc, True, True)

        streamingBody, flag = manageRemoteS3.getFileStreamingBody(fileKeyEnc)
        decryptionAdapter = EncryptionAdapter(streamingBody)
        decryptionAdapter.setDebugLogger(logging)
        decryptionAdapter.setupDecryptOnRead(base64.b64decode(manageRemoteS3.aesEncryptionKey))

        self.compareFiles(file_path, decryptionAdapter, chunksize)

        if not keep:
            print(f'###############################\ndeleting files\n###############################')
            manageLocalS3.deleteFile(fileKey)
            manageRemoteS3.deleteFile(fileKeyEnc)

    ##############################################
    def _logMemInfo(self,comment=""):
        """
            Print memory info with a comment to the debug logger if it is set

            :param comment: The comment to print
            :type comment: str
        """
        if not self.debugLogger:
            return
        
        self.debugLogger.debug(f'Current memory usage: {psutil.Process().memory_info().rss / 1024 / 1024} MB | {comment}')


    ##############################################
    def compareFiles(self, file_path, decryptionAdapter:EncryptionAdapter, chunksize:int = 5*1024*1024):
        """
        Compare two files

        :param file_path: The path to the file to compare
        :type file_path: str
        :param decryptionAdapter: The adapter to read the file from
        :type decryptionAdapter: EncryptionAdapter
        :param chunksize: The size of the chunks to compare
        :type chunksize: int
        :return: True if the files are the same, False if not
        :rtype: bool
        """
        with open(file_path, 'rb') as original_file:

            chunkCounter = 0
            while True:
                chunkDownload = decryptionAdapter.read(chunksize)
                chunkOriginal = original_file.read(chunksize)
                self._logMemInfo("After reading chunk online and from file")
                if not chunkDownload == chunkOriginal:
                    print(f"Chunk #{chunkCounter} is not the same in both files aborting")
                    return False

                if not chunkDownload and not chunkOriginal:
                    print(
                        f"Both file chunks are empty now - until now both files are the same - totally read {chunkCounter} chunks")
                    return True


                if not chunkDownload and chunkOriginal:
                    print(f"downloaded file is smaller than original file")
                    return False

                if chunkDownload and not chunkOriginal:
                    print(f"downloaded file is bigger than original file")
                    return False

                self._logMemInfo(f'completed chunk {chunkCounter} successfully')
                chunkCounter += 1