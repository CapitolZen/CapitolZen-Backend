from django.http import JsonResponse

from rest_framework import status


def index(request):
    return JsonResponse({'status': status.HTTP_200_OK,
                         'message': 'Backend API'},
                        status=status.HTTP_200_OK)


def page_not_found_view(request):
    return JsonResponse({'status': status.HTTP_404_NOT_FOUND,
                         'message': 'Page Not Found'},
                        status=status.HTTP_404_NOT_FOUND)


def error_view(request):
    return JsonResponse({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Application Error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def permission_denied_view(request):
    return JsonResponse({'status': status.HTTP_403_FORBIDDEN,
                         'message': 'Permission Denied'},
                        status=status.HTTP_403_FORBIDDEN)


def bad_request_view(request):
    return JsonResponse({'status': status.HTTP_400_BAD_REQUEST,
                         'message': 'Bad Request'},
                        status=status.HTTP_400_BAD_REQUEST)
