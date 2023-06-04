from django.db import models

class IPAdressLastReqTime(models.Model):
    IP_address = models.GenericIPAddressField(null=False, unique=True, primary_key=True)
    last_req_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.last_req_time = self.last_req_time.replace(tzinfo=None)
        super(IPAdressLastReqTime, self).save(*args, **kwargs)


# adr = IPAdressLastReqTime()
# adr.asave(update_fields='last_req_time')
