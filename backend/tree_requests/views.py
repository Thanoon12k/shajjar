from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.services import notify

from .forms import TreeRequestForm
from .models import TreeRequest, TreeRequestImage


@login_required
def new_request(request):
    initial = {"city": request.user.city, "district": request.user.district, "contact_phone": request.user.phone_number}
    form = TreeRequestForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            for f in form.cleaned_data["photos"]:
                TreeRequestImage.objects.create(tree_request=obj, image=f)
        notify(
            request.user,
            f"تم استلام طلبك {obj.request_code} 🌱",
            "فريق #شجّر راح يراجع الطلب ويتواصل وياك.",
            type="request",
            link=obj.get_absolute_url(),
            obj=obj,
        )
        messages.success(request, f"تم استلام طلبك — رقم الطلب: {obj.request_code}")
        return redirect(obj.get_absolute_url() + "?new=1")
    return render(request, "tree_requests/new.html", {"form": form})


@login_required
def my_requests(request):
    items = request.user.tree_requests.all()
    return render(request, "tree_requests/list.html", {"items": items})


@login_required
def detail(request, code):
    obj = get_object_or_404(TreeRequest.objects.select_related("preferred_species"), request_code=code)
    if obj.user_id != request.user.pk and not request.user.is_team:
        raise Http404
    return render(request, "tree_requests/detail.html", {"obj": obj, "is_new": request.GET.get("new") == "1"})
