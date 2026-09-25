from django.conf import settings

THEMES = [
    ("hadba", "غابة الحدباء", "#1f5130"),
    ("dijla", "دجلة", "#0f5c63"),
    ("nabk", "نبك وطين", "#8a5a2b"),
    ("rumman", "رمّان نينوى", "#9b2335"),
    ("night", "ليل الموصل", "#0d1712"),
]


def shajjar(request):
    unread = 0
    if request.user.is_authenticated:
        unread = request.user.notifications.filter(is_read=False).count()
    return {
        "THEMES": THEMES,
        "MAP_CENTER": settings.MAP_CENTER,
        "MAP_ZOOM": settings.MAP_ZOOM,
        "unread_notifications": unread,
        "DEMO_MODE": settings.DEMO_MODE,
    }
