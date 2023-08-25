from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class login(MiddlewareMixin):
    def process_request(self, request):
        login_status = request.COOKIES.get("login_status")
        login_seession = request.session.get(login_status)
        if request.path_info != '/':
            if (not login_status or not login_seession) or login_seession != login_status:
                return redirect("/")
        return None
