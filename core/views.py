from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def home_view(request):
    """Home page view"""
    context = {
        'user': request.user,
        'is_member': request.user.groups.filter(name='members').exists() if request.user.is_authenticated else False,
    }
    return render(request, 'core/home.html', context)


@login_required
def members_only_view(request):
    """View for members-only content"""
    if not request.user.groups.filter(name='members').exists():
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied. Members only.")
    
    context = {
        'user': request.user,
        'exclusive_content': "This is exclusive content for members only!",
    }
    return render(request, 'core/members_only.html', context)
