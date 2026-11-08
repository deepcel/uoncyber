from .models import Notification


def notify(user, title, message, link=''):
    """Create one in-app notification for a user."""
    return Notification.objects.create(user=user, title=title, message=message, link=link)


def notify_many(users, title, message, link=''):
    """The same notification for several users, in one query."""
    return Notification.objects.bulk_create([
        Notification(user=user, title=title, message=message, link=link)
        for user in users
    ])
