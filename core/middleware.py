from django.utils import timezone
from core.models import VisitorLog

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not (request.path.startswith('/admin/') or 
                request.path.startswith('/static/') or 
                request.path.startswith('/media/') or 
                request.path.startswith('/dashboard/')):
            
            ip = self.get_client_ip(request)
            today = timezone.now().date()

            if ip and not VisitorLog.objects.filter(ip_address=ip, visited_date=today).exists():
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                VisitorLog.objects.create(ip_address=ip, user_agent=user_agent)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip