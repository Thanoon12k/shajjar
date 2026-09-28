from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.services import notify

from .models import Campaign, CampaignParticipant

VISIBLE = [Campaign.Status.PUBLISHED, Campaign.Status.REGISTRATION_CLOSED, Campaign.Status.ACTIVE, Campaign.Status.COMPLETED]


def campaign_list(request):
    qs = Campaign.objects.filter(status__in=VISIBLE).annotate(
        n=Count("participants", filter=~Q(participants__status=CampaignParticipant.Status.CANCELLED))
    )
    now = timezone.now()
    upcoming = qs.filter(start_date__gte=now - timezone.timedelta(hours=12)).exclude(status=Campaign.Status.COMPLETED).order_by("start_date")
    past = qs.filter(Q(status=Campaign.Status.COMPLETED) | Q(start_date__lt=now - timezone.timedelta(hours=12))).order_by("-start_date")
    return render(request, "campaigns/list.html", {"upcoming": upcoming, "past": past[:12]})


def detail(request, pk):
    c = get_object_or_404(Campaign, pk=pk, status__in=VISIBLE)
    me = None
    if request.user.is_authenticated:
        me = c.participants.filter(user=request.user).exclude(status=CampaignParticipant.Status.CANCELLED).first()
    return render(request, "campaigns/detail.html", {"c": c, "me": me, "count": c.active_participants.count()})


@login_required
@require_POST
def join(request, pk):
    c = get_object_or_404(Campaign, pk=pk)
    existing = c.participants.filter(user=request.user).first()
    if existing and existing.status != CampaignParticipant.Status.CANCELLED:
        messages.info(request, "أنت مسجّل مسبقاً بهذه الحملة.")
    elif not c.registration_open:
        messages.error(request, "التسجيل بهذه الحملة مغلق.")
    else:
        if existing:
            existing.status = CampaignParticipant.Status.REGISTERED
            existing.save(update_fields=["status"])
        else:
            CampaignParticipant.objects.create(campaign=c, user=request.user)
        notify(request.user, f"تم تسجيلك بحملة {c.title} 🤝", f"الموعد: {timezone.localtime(c.start_date):%Y/%m/%d %H:%M}", type="campaign", link=c.get_absolute_url(), obj=c)
        messages.success(request, "تم تسجيلك! نشوفك بالحملة 🌳")
    return redirect(c.get_absolute_url())


@login_required
@require_POST
def leave(request, pk):
    c = get_object_or_404(Campaign, pk=pk)
    p = c.participants.filter(user=request.user).first()
    if p and p.status in (CampaignParticipant.Status.REGISTERED, CampaignParticipant.Status.APPROVED):
        p.status = CampaignParticipant.Status.CANCELLED
        p.save(update_fields=["status"])
        messages.info(request, "تم إلغاء مشاركتك.")
    return redirect(c.get_absolute_url())
