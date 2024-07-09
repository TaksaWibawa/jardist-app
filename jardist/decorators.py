from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from functools import wraps

def login_and_group_required(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='login')
        def _wrapped_view(request, *args, **kwargs):
            if not group_names:
                return view_func(request, *args, **kwargs)
            group_query = Q()
            for name in group_names:
                group_query |= Q(name__iexact=name)
            if not request.user.groups.filter(group_query).exists():
                messages.error(request, "You do not have permission to access this page.")
                return HttpResponse("Unauthorized", status=401)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator