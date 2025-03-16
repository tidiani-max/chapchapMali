import pytz
from django.utils.timezone import activate

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timezone = request.COOKIES.get('user_timezone')
        if timezone:
            try:
                activate(pytz.timezone(timezone))
            except pytz.UnknownTimeZoneError:
                activate(pytz.UTC)  # Default to UTC if invalid
        return self.get_response(request)
