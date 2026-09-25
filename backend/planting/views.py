from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from trees.models import Tree

from .models import PlantingSite


def map_view(request):
    cities = PlantingSite.objects.values_list("city", flat=True).distinct().order_by("city")
    return render(request, "planting/map.html", {"cities": cities, "kinds": PlantingSite.Kind.choices})


def map_data(request):
    sites = PlantingSite.objects.exclude(status=PlantingSite.Status.INACTIVE).prefetch_related("species")
    city = request.GET.get("city")
    if city:
        sites = sites.filter(city=city)
    features = []
    for s in sites:
        features.append(
            {
                "type": "site",
                "id": s.pk,
                "name": s.name,
                "kind": s.kind,
                "kind_label": s.get_kind_display(),
                "lat": float(s.latitude),
                "lng": float(s.longitude),
                "health": s.health,
                "trees": s.total_trees,
                "species": "، ".join(sp.arabic_name for sp in s.species.all()),
                "date": s.planting_date.strftime("%m/%Y") if s.planting_date else "",
                "watering": s.watering_entity,
                "status": s.get_status_display(),
                "rate": s.survival_rate,
                "url": s.get_absolute_url(),
                "district": s.district,
                "city": s.city,
            }
        )
    trees = (
        Tree.objects.filter(status=Tree.Status.ACTIVE, site__isnull=True)
        .exclude(Q(latitude__isnull=True) | Q(longitude__isnull=True))
        .select_related("species")[:2000]
    )
    health_map = {"excellent": "good", "good": "good", "needs_care": "attention", "damaged": "damaged", "dead": "damaged"}
    for t in trees:
        features.append(
            {
                "type": "tree",
                "name": t.tree_code,
                "lat": float(t.latitude),
                "lng": float(t.longitude),
                "health": health_map.get(t.health_status, "good"),
                "species": t.species.arabic_name,
                "status": t.get_health_status_display(),
                "url": t.get_absolute_url(),
                "district": t.place,
            }
        )
    return JsonResponse({"features": features})


def site_detail(request, pk):
    site = get_object_or_404(PlantingSite.objects.prefetch_related("species", "batches__species"), pk=pk)
    return render(request, "planting/site.html", {"site": site, "trees": site.trees.select_related("species")[:24]})
