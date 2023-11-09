from django.core import mail
from django.conf import settings



class KissMailer():
    '''
        later add some other stuff and configuration things as well as perhaps a html template.
        for now just send a mail via default django smtp sendmail
    '''

    def __init__(self):
        pass

    def sendmail(self, to, subject, message):
        import logging
        logger = logging.getLogger("django_debug")
        logger.info(f'creating mail to {to} with subject {subject} and message {message}')
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
