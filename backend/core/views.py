from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from campaigns.models import Campaign, CampaignParticipant
from content.models import ContentArticle
from planting.models import PlantingSite
from reports.models import EnvironmentalReport
from species.models import TreeSpecies
from tree_requests.models import TreeRequest
from trees.models import Health, Tree

from .models import Notification
from .stats import dashboard_stats, impact_stats, survival_rate


def home(request):
    now = timezone.now()
    ctx = {
        "stats": impact_stats(),
        "campaigns": Campaign.objects.filter(status=Campaign.Status.PUBLISHED, start_date__gte=now).order_by("start_date")[:3],
        "sites": PlantingSite.objects.exclude(status=PlantingSite.Status.INACTIVE).prefetch_related("species")[:6],
        "stories": ContentArticle.published.select_related("category").filter(category__slug="field")[:4],
        "articles": ContentArticle.published.select_related("category").exclude(category__slug="field").filter(category__is_legal=False)[:3],
        "species": TreeSpecies.objects.filter(is_active=True).order_by("-heat_tolerance", "-drought_tolerance")[:4],
    }
    return render(request, "core/home.html", ctx)


def impact(request):
    stats = impact_stats()
    by_city = (
        PlantingSite.objects.values("city")
        .annotate(n=Sum("total_trees"), alive=Sum("alive_trees"), sites=Count("id"))
        .order_by("-n")
    )
    by_kind = PlantingSite.objects.values("kind").annotate(n=Sum("total_trees")).order_by("-n")
    kind_labels = dict(PlantingSite.Kind.choices)
    max_n = max([r["n"] or 0 for r in by_city] + [1])
    return render(
        request,
        "core/impact.html",
        {
            "stats": stats,
            "by_city": [{**r, "pct": (r["n"] or 0) / max_n * 100, "rate": survival_rate(r["alive"] or 0, r["n"] or 0)} for r in by_city],
            "by_kind": [{"label": kind_labels.get(r["kind"], r["kind"]), "n": r["n"] or 0} for r in by_kind],
        },
    )


def about(request):
    return render(request, "core/about.html", {"stats": impact_stats()})


@login_required
def activity(request):
    u = request.user
    trees = Tree.objects.filter(Q(owner=u) | Q(caretaker=u)).select_related("species").distinct()
    parts = u.participations.exclude(status=CampaignParticipant.Status.CANCELLED).select_related("campaign")
    agg = parts.aggregate(trees=Sum("trees_planted"), hours=Sum("volunteer_hours"))
    ctx = {
        "trees": trees[:6],
        "tree_count": trees.count(),
        "requests": u.tree_requests.all()[:5],
        "reports": u.reports.all()[:5],
        "participations": parts.order_by("-campaign__start_date")[:5],
        "vol": {
            "campaigns": parts.filter(status__in=["attended", "completed"]).count(),
            "trees": agg["trees"] or 0,
            "hours": agg["hours"] or 0,
            "registered": parts.count(),
        },
        "notifications": u.notifications.all()[:5],
    }
    return render(request, "core/activity.html", ctx)


@login_required
def notifications(request):
    items = request.user.notifications.all()[:100]
    return render(request, "core/notifications.html", {"items": items})


@login_required
@require_POST
def notification_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save(update_fields=["is_read"])
    return redirect(n.link or "core:notifications")


@login_required
@require_POST
def notifications_read_all(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "تم تعليم كل الإشعارات كمقروءة.")
    return redirect("core:notifications")


def _is_team(user):
    return user.is_authenticated and user.is_team


@user_passes_test(_is_team, login_url="accounts:login")
def dashboard(request):
    city = request.GET.get("city") or ""
    district = request.GET.get("district") or ""
    year = request.GET.get("year") or ""
    sites = PlantingSite.objects.all()
    trees = Tree.objects.select_related("species", "site")
    if city:
        sites = sites.filter(city=city)
        trees = trees.filter(Q(site__city=city) | Q(request__city=city))
    if district:
        sites = sites.filter(district=district)
        trees = trees.filter(Q(site__district=district) | Q(request__district=district) | Q(location_label__icontains=district))
    if year.isdigit():
        sites = sites.filter(planting_date__year=int(year))
        trees = trees.filter(planting_date__year=int(year))
    s = sites.aggregate(total=Sum("total_trees"), alive=Sum("alive_trees"), damaged=Sum("damaged_trees"), dead=Sum("dead_trees"))
    solo = trees.filter(site__isnull=True)
    solo_dead = solo.filter(Q(status=Tree.Status.DEAD) | Q(health_status=Health.DEAD)).count()
    solo_damaged = solo.filter(health_status=Health.DAMAGED).count()
    planted = (s["total"] or 0) + solo.count()
    alive = (s["alive"] or 0) + solo.count() - solo_dead
    filtered = {
        "planted": planted,
        "alive": alive,
        "damaged": (s["damaged"] or 0) + solo_damaged,
        "dead": (s["dead"] or 0) + solo_dead,
        "rate": survival_rate(alive, planted),
    }
    req_labels = dict(TreeRequest.Status.choices)
    rep_labels = dict(EnvironmentalReport.Status.choices)
    stats = dashboard_stats()
    ctx = {
        "stats": stats,
        "f": filtered,
        "req_status": [(req_labels.get(r["status"]), r["n"]) for r in stats["requests_by_status"]],
        "rep_status": [(rep_labels.get(r["status"]), r["n"]) for r in stats["reports_by_status"]],
        "sites": sites.order_by("-planting_date")[:50],
        "trees": trees.order_by("-planting_date")[:30],
        "requests": TreeRequest.objects.select_related("user").filter(status__in=["submitted", "under_review", "approved", "ready_for_distribution"])[:10],
        "reports": EnvironmentalReport.objects.filter(status__in=["submitted", "under_review", "verified", "in_progress", "forwarded"]).order_by("-priority", "-created_at")[:10],
        "cities": PlantingSite.objects.values_list("city", flat=True).distinct().order_by("city"),
        "districts": PlantingSite.objects.exclude(district="").values_list("district", flat=True).distinct().order_by("district"),
        "years": sorted({d.year for d in PlantingSite.objects.exclude(planting_date=None).values_list("planting_date", flat=True)}, reverse=True),
        "sel": {"city": city, "district": district, "year": year},
    }
    return render(request, "core/dashboard.html", ctx)
