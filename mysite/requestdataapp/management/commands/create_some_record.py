from django.core.management import BaseCommand

from requestdataapp.models import IPAdressLastReqTime

class Command(BaseCommand):
    """
    Создаем тестовый запись в БД
    """
    
    def handle(self, *args, **options):
        self.stdout.write("Create IP record")
        
        IP_list = ['192.168.0.1', '192.168.1.1']
        
        for IP_line in IP_list:
            IP_record, created = IPAdressLastReqTime.objects.get_or_create(IP_address=IP_line)
            self.stdout.write(f'Created IP_record {IP_line}')
        self.stdout.write(self.style.SUCCESS("Record made"))