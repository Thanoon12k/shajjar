from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.services import notify

from .forms import ReportForm
from .models import EnvironmentalReport, EnvironmentalReportMedia

HOURLY_REPORT_LIMIT = 5


@login_required
def new_report(request):
    form = ReportForm(request.POST or None, request.FILES or None, initial={"city": request.user.city})
    if request.method == "POST":
        recent = EnvironmentalReport.objects.filter(
            reporter=request.user, created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        if recent >= HOURLY_REPORT_LIMIT and not request.user.is_team:
            messages.error(request, "وصلت الحد الأعلى للبلاغات خلال ساعة. حاول بعد قليل.")
        elif form.is_valid():
            with transaction.atomic():
                obj = form.save(commit=False)
                obj.reporter = request.user
                if obj.category == EnvironmentalReport.Category.FIRE:
                    obj.priority = EnvironmentalReport.Priority.URGENT
                obj.save()
                for f in form.cleaned_data["photos"]:
                    EnvironmentalReportMedia.objects.create(report=obj, file=f)
            notify(request.user, f"وصلنا بلاغك {obj.report_code} 🚨", "شكراً لأنك تحمي بيئتنا.", type="report", link=obj.get_absolute_url(), obj=obj)
            messages.success(request, f"تم إرسال البلاغ — رقم البلاغ: {obj.report_code}")
            return redirect(obj.get_absolute_url())
    return render(request, "reports/new.html", {"form": form})


@login_required
def my_reports(request):
    return render(request, "reports/list.html", {"items": request.user.reports.all()})


@login_required
def detail(request, code):
    obj = get_object_or_404(EnvironmentalReport, report_code=code)
    if obj.reporter_id != request.user.pk and not request.user.is_team:
        raise Http404
    stages = ["🟡 تم الاستلام", "🔵 قيد المتابعة", "🟢 تمت المعالجة"]
    return render(request, "reports/detail.html", {"obj": obj, "stages": stages})
