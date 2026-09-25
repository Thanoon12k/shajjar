from .models import AuditLog, Notification


def audit(actor, action, obj, **metadata):
    AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        object_type=obj._meta.label,
        object_id=str(obj.pk),
        metadata=metadata,
    )


def notify(user, title, body="", type=Notification.Type.GENERAL, link="", obj=None):
    if user is None:
        return None
    return Notification.objects.create(
        user=user,
        title=title,
        body=body,
        type=type,
        link=link,
        related_object_type=obj._meta.label if obj is not None else "",
        related_object_id=obj.pk if obj is not None else None,
    )
