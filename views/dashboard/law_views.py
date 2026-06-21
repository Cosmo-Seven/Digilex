from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import LawModel
from utils.decorators import custom_login_required
from constants.message import CREATE, UPDATE, DELETE

@custom_login_required("dashboard_login")
def law_list(request):
    laws = LawModel.objects.all()
    return render(request, "dashboard/law_list.html", {"laws": laws})

@custom_login_required("dashboard_login")
def law_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        icon = request.FILES.get("icon")
        is_free = request.POST.get("is_free") == "on"
        law = LawModel.objects.create(
            title=title,
            description=description,
            icon=icon,
            is_free=is_free,
            )
        law.save()
        messages.success(request, CREATE)
        return redirect("law_list")

@custom_login_required("dashboard_login")
def law_update(request, id):
    law = get_object_or_404(LawModel, id=id)
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        icon = request.FILES.get("icon")
        law.title = title
        law.description = description
        if icon:
            law.icon = icon
        law.is_free = request.POST.get("is_free") == "on"
        law.save()
        messages.success(request, UPDATE)
        return redirect("law_list")

@custom_login_required("dashboard_login")
def law_delete(request, id):
    law = get_object_or_404(LawModel, id=id)
    if law.icon:
        law.icon.delete()
    law.delete()
    messages.success(request, DELETE)
    return redirect("law_list")

