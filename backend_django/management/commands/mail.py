from django.core.management.base import BaseCommand

from backend_django.services.mailer import KissMailer

class Command(BaseCommand):
    help = 'sends a test mail to see if config is correct'

    def add_arguments(self, parser):
        parser.add_argument('to', type=str, help='the mail address to send the test mail to')

    def handle(self, *args, **options):
        mailer = KissMailer()
        mailer.sendmail(options['to'], 'test mail', 'this is a test mail')



