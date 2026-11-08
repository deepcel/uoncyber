from .models import AuditLog


def client_ip(request):
    # REMOTE_ADDR is the direct peer. Behind a reverse proxy, configure the proxy
    # to set it correctly rather than trusting a client-supplied X-Forwarded-For.
    return request.META.get('REMOTE_ADDR') or '0.0.0.0'


def log_event(request, action, user=None, **details):
    """Record a security-relevant event. `user` is the actor; anything about a target goes in details."""
    return AuditLog.objects.create(
        user=user,
        action=action,
        ip_address=client_ip(request),
        details=details
    )
