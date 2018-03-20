from django.utils.functional import SimpleLazyObject
from capitolzen.organizations.models import Organization
from capitolzen.groups.models import Page


def get_organization(request):
    if request.user is None:
        return None

    organization_id = request.META.get('HTTP_X_ORGANIZATION')
    if organization_id is None:
        return None

    organization = Organization.objects.filter(id=organization_id, users=request.user).first()

    if not organization:
        return None

    return organization


class ActiveOrganizationMiddleware(object):
    """
    Using a header, inject the current organization into the middleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        request.organization = SimpleLazyObject(lambda: get_organization(request))


def get_page_dependencies(request):
    page_id = request.META.get('HTTP_X_PAGE')
    if page_id is None:
        return None

    try:
        page = Page.objects.get(id=page_id)
        if str(page.organization.id) != request.META.get('HTTP_X_ORGANIZATION'):
            return None
        if page.visibility == 'anyone':
            return None
        else:
            return {
                "page": page,
                "group": page.group
            }

    except Exception:
        return None


class PageAccessMiddleWare(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        data = get_page_dependencies(request)
        if data:
            request.page = data['page']
            request.group = data['group']
