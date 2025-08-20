from django.http import HttpResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

@csrf_exempt
@staff_member_required
def metrics_view(request):
    """
    Prometheus scrape endpoint
    Only staff/admin users can access.
    """
    data = generate_latest()
    return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)
