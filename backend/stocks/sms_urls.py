"""
SMS URL configuration and stub handlers.
If SMS is not configured, these endpoints return success=false with a helpful message.
"""
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

app_name = 'sms'


def _not_configured_response(action: str):
    return JsonResponse({
        'success': False,
        'message': f'SMS {action} not configured on this server',
        'code': 'SMS_NOT_CONFIGURED'
    }, status=200)


@csrf_exempt
def request_code(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    # TODO: Integrate provider (e.g., Twilio) here
    return _not_configured_response('request')


@csrf_exempt
def verify_code(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    # TODO: Implement verification logic against stored codes
    return _not_configured_response('verify')


@csrf_exempt
def send_test(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    # TODO: Implement test send logic when provider is configured
    return _not_configured_response('send')


urlpatterns = [
    path('request-code/', request_code, name='request_code'),
    path('verify/', verify_code, name='verify_code'),
    path('send-test/', send_test, name='send_test'),
]
