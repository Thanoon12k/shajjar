from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum

from planting.models import PlantingSite
from reports.models import EnvironmentalReport
from tree_requests.models import TreeRequest
from trees.models import Health, Tree


def survival_rate(alive, total):
    return round(alive / total * 100, 1) if total else 0


def impact_stats():
    """Headline numbers. Site-level counts cover group plantings (forests, streets);
    individually registered trees are counted on top of them."""
    site_totals = PlantingSite.objects.aggregate(
        total=Sum("total_trees"), alive=Sum("alive_trees"), damaged=Sum("damaged_trees"), dead=Sum("dead_trees")
    )
    ind = Tree.objects.filter(site__isnull=True).aggregate(
        total=Count("id"),
        dead=Count("id", filter=Q(status=Tree.Status.DEAD) | Q(health_status=Health.DEAD)),
        damaged=Count("id", filter=Q(health_status=Health.DAMAGED)),
    )
    total = (site_totals["total"] or 0) + ind["total"]
    dead = (site_totals["dead"] or 0) + ind["dead"]
    damaged = (site_totals["damaged"] or 0) + ind["damaged"]
    alive = (site_totals["alive"] or 0) + (ind["total"] - ind["dead"])
    volunteers = (
        get_user_model()
        .objects.filter(Q(role="volunteer") | Q(participations__isnull=False))
        .distinct()
        .count()
    )
    followed = Tree.objects.filter(status=Tree.Status.ACTIVE).count()
    return {
        "trees": total,
        "alive": alive,
        "damaged": damaged,
        "dead": dead,
        "survival_rate": survival_rate(alive, total),
        "sites": PlantingSite.objects.exclude(status=PlantingSite.Status.INACTIVE).count(),
        "volunteers": volunteers,
        "followed": followed,
    }


def dashboard_stats():
    stats = impact_stats()
    stats.update(
        {
            "pending_requests": TreeRequest.objects.filter(
                status__in=[TreeRequest.Status.SUBMITTED, TreeRequest.Status.UNDER_REVIEW]
            ).count(),
            "needs_care": Tree.objects.filter(
                status=Tree.Status.ACTIVE, health_status__in=[Health.NEEDS_CARE, Health.DAMAGED]
            ).count()
            + PlantingSite.objects.filter(status=PlantingSite.Status.NEEDS_ATTENTION).count(),
            "new_reports": EnvironmentalReport.objects.filter(status=EnvironmentalReport.Status.SUBMITTED).count(),
            "reports_by_status": list(
                EnvironmentalReport.objects.values("status").annotate(n=Count("id")).order_by("-n")
            ),
            "requests_by_status": list(TreeRequest.objects.values("status").annotate(n=Count("id")).order_by("-n")),
        }
    )
    return stats
