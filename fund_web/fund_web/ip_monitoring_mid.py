import time
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class Ipmonitoring(MiddlewareMixin):
    def process_request(self, request):
        request_num = 5
        request_ip = request.META['REMOTE_ADDR']

        if not request_ip or request.path_info == "/error/":
            return None
        now_date = time.time()
        is_request = cache.get(request_ip)
        if not is_request:
            cache.set(request_ip, [now_date], 60)
        else:
            last_date = is_request[0]
            if now_date - last_date <= 60 and len(is_request) >= request_num:
                return redirect("Error")

            if now_date - last_date >= 60:
                cache.set(request_ip, [now_date], 60)

            else:
                is_request.append(now_date)
                cache.set(request_ip, is_request, 60 - (now_date - last_date))

        return None
