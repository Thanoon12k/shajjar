import io

import segno
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.services import notify

from .forms import TreeUpdateForm
from .models import Tree


@login_required
def my_trees(request):
    trees = (
        Tree.objects.filter(Q(owner=request.user) | Q(caretaker=request.user))
        .select_related("species", "site")
        .distinct()
    )
    return render(request, "trees/my.html", {"trees": trees})


def detail(request, code):
    tree = get_object_or_404(Tree.objects.select_related("species", "site", "owner", "caretaker"), tree_code=code)
    updates = tree.updates.select_related("user").order_by("created_at")
    return render(
        request,
        "trees/detail.html",
        {"tree": tree, "updates": updates, "can_update": tree.is_followed_by(request.user)},
    )


def lookup(request):
    code = (request.GET.get("code") or "").strip().upper()
    if code and not code.startswith("SHJ-") and code.isdigit():
        code = f"SHJ-{int(code):06d}"
    if code and Tree.objects.filter(tree_code=code).exists():
        return redirect("trees:detail", code=code)
    if code:
        messages.error(request, f"ما لقينا شجرة بالرمز {code}")
    return redirect(request.META.get("HTTP_REFERER") or "core:home")


@login_required
def add_update(request, code):
    tree = get_object_or_404(Tree, tree_code=code)
    if not tree.is_followed_by(request.user):
        return HttpResponseForbidden("فقط راعي الشجرة أو فريق #شجّر يكدر يضيف متابعة.")
    form = TreeUpdateForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        upd = form.save(commit=False)
        upd.tree = tree
        upd.user = request.user
        upd.created_at = timezone.now()
        if request.user.is_team:
            upd.verified, upd.verified_by = True, request.user
        upd.save()
        upd.apply_to_tree()
        messages.success(request, "شكراً! تم تسجيل متابعة الشجرة 🌳")
        if tree.owner and tree.owner != request.user:
            notify(tree.owner, f"تحديث جديد لشجرتك {tree.tree_code}", type="tree", link=tree.get_absolute_url(), obj=tree)
        return redirect(tree.get_absolute_url())
    return render(request, "trees/update.html", {"tree": tree, "form": form})


def qr_svg(request, code):
    tree = get_object_or_404(Tree, tree_code=code)
    url = settings.SITE_URL.rstrip("/") + tree.get_absolute_url()
    qr = segno.make(url, error="m")
    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=6, dark="#16351f", light="#ffffff", border=2, xmldecl=False)
    resp = HttpResponse(buf.getvalue(), content_type="image/svg+xml")
    if request.GET.get("download"):
        resp["Content-Disposition"] = f'attachment; filename="{tree.tree_code}.svg"'
    return resp
