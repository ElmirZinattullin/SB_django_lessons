from django.http import HttpRequest
import datetime

# from models import IPAdressLastReqTime
from requestdataapp.models import IPAdressLastReqTime


def set_useragent_on_request_middleware(get_response):

    print('Initial call')
    def middleware(request: HttpRequest):
        print('Before get response')
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print('after get response')
        return response

    return middleware


def throttling_middleware(some_response):

    print('Initial call')
    def middleware(request: HttpRequest):
        print('Before get response')
        META_dict = request.META
        IP_adress = META_dict['REMOTE_ADDR']
        IP_record, created = IPAdressLastReqTime.objects.get_or_create(IP_address=IP_adress)
        min_timedelta = datetime.timedelta(seconds=1)
        if not created:
            deltatime = datetime.datetime.now() - IP_record.last_req_time.replace(tzinfo=None)
            print(IP_record.last_req_time.replace(tzinfo=None))
            if deltatime < min_timedelta:
                # print("Вы делаете слишком частые запросы")
                raise Exception("Вы делаете слишком частые запросы. Последний запрос в",
                                str(IP_record.last_req_time.replace(tzinfo=None)))
            IP_record.last_req_time = datetime.datetime.now()
            IP_record.save()
        response = some_response(request)
        return response
    return middleware


class CountRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request:HttpRequest):
        self.requests_count += 1
        print('requests count =', self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print("response count=", self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exceptions: Exception):
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions so far")