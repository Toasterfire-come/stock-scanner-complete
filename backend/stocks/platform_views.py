import platform
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from django.utils import timezone


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def platform_stats_api(request):
    try:
        data = {
            'time': timezone.now().isoformat(),
            'python_version': platform.python_version(),
            'system': platform.system(),
            'release': platform.release(),
            'node': platform.node(),
        }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Failed to get platform stats'}, status=500)

