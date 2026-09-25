from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "شجّر — لوحة الإدارة"
admin.site.site_title = "شجّر"
admin.site.index_title = "إدارة منصة #شجّر"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("map/", include("planting.urls")),
    path("species/", include("species.urls")),
    path("trees/", include("trees.urls")),
    path("requests/", include("tree_requests.urls")),
    path("reports/", include("reports.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("learn/", include("content.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
