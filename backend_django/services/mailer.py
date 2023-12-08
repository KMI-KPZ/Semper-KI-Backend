from django.core import mail
from django.conf import settings



class KissMailer():
    """
        later add some other stuff and configuration things as well as perhaps a html template.
        for now just send a mail via default django smtp sendmail
    """

    def sendmail(self, to, subject, message):
        """
        :param self: mailer object
        :type self: KissMailer
        :param to: recipient email address (1 only)
        :type to: str
        :param subject: subject of the mail
        :type subject: str
        :param message: message of the mail
        :type message: str
        :return: number of sent emails or False on failure
        :rtype: int or bool
        """
        import logging
        logger = logging.getLogger("django_debug")
        logger.debug(f'creating mail to {to} with subject {subject} and message {message}')
        try:
            connection = mail.get_connection()
            email = mail.send_mail(
                subject,
                message,
                settings.EMAIL_ADDR_SUPPORT,
                [to], False,
                connection=connection)
            return email
        except Exception as e:
            logging.error(f'error sending mail: {e}')
            return False
