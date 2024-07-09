"""
Part of Semper-KI software

Silvio Weging 2024

Contains: Class for managing the locales-file
"""
import logging, json
from django.conf import settings

from Generic_Backend.code_General.connections.redis import RedisConnection

loggerError = logging.getLogger("errors")

##################################################################
class ManageTranslations():
    """
    Manages the translations of certain keys saved into the translations.json
    
    """

    
    #######################################################
    def __init__(self, filePathAndName) -> None:
        """
        Retrieve translations from file and save it into redis 

        :param filePathAndName: the very same
        :type filePathAndName: str
        :return: Nothing
        :rtype: None
        
        """

        self.filePathAndName = filePathAndName
        self.redisCon = RedisConnection()
        self.retrieveContentFromRedis(initial=True)

    #######################################################
    def retrieveContentFromRedis(self, initial=False) -> str:
        """
        Check if the key is inside redis, if it is, take it from there, if not, save it for faster access

        :return: The translation as JSON
        :rtype: str

        """
        translations, exists = self.redisCon.retrieveContentJSON(self.filePathAndName)
        if not exists or initial:
            with open(str(settings.BASE_DIR) + self.filePathAndName) as translationsFile:
                translationsFileContent = json.loads(translationsFile.read())
                self.redisCon.addContentJSON(self.filePathAndName, translationsFileContent, True)
                return translationsFileContent
        else:
            return translations



    #######################################################
    def getTranslation(self, locale:str, keyArr:list[str]) -> str:
        """
        Get the correct translation for a certain list of keys from the json

        :param locale: The locale string retrieved from either the profile or the session
        :type locale: str
        :param keyArr: path to take inside the json e.g. email, subjects, confirmedByClient
        :type keyArr: list[str]
        :return: The correct word/sentence
        :rtype: str
        """

        try:
            translationObj = self.retrieveContentFromRedis()
            path = translationObj[locale]
            for key in keyArr: # got through the levels
                path = path[key]
            return path
        except Exception as error:
            loggerError.error(f"getTranslation: {str(error)}")
            return "ERROR"

##################################################################
manageTranslations = ManageTranslations("/code_SemperKI/translations.json")