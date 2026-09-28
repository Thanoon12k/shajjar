from django.shortcuts import get_object_or_404, render

from .models import TreeSpecies

PLACES = [
    ("streets", "🛣️ رصيف / شارع"),
    ("gardens", "🏠 بيت / حديقة"),
    ("farms", "🌾 بستان"),
    ("public_spaces", "🌲 غابة / مكان عام"),
]
SUN = [("strong", "☀️ شمس قوية طول اليوم"), ("partial", "⛅ شمس جزئية")]
WATER = [("low", "💧 ماء قليل"), ("medium", "💧💧 ماء متوسط"), ("high", "💧💧💧 ماء متوفر")]


def encyclopedia(request):
    place = request.GET.get("place") or None
    sun = request.GET.get("sun") or None
    water = request.GET.get("water") or None
    species = list(TreeSpecies.objects.filter(is_active=True))
    asked = any([place, sun, water])
    for s in species:
        s.stars = s.match_score(place, sun, water)
    if asked:
        species.sort(key=lambda s: -s.stars)
    return render(
        request,
        "species/list.html",
        {
            "species": species,
            "asked": asked,
            "places": PLACES,
            "suns": SUN,
            "waters": WATER,
            "sel": {"place": place, "sun": sun, "water": water},
        },
    )


def detail(request, pk):
    sp = get_object_or_404(TreeSpecies, pk=pk, is_active=True)
    return render(request, "species/detail.html", {"sp": sp, "sites": sp.sites.all()[:6]})
