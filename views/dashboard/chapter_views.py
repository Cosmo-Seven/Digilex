from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import LawModel, ChapterModel
from utils.decorators import custom_login_required
from constants.message import CREATE, UPDATE, DELETE

@custom_login_required("dashboard_login")
def chapter_list(request, law_id):
    law = get_object_or_404(LawModel, id=law_id)
    chapters = ChapterModel.objects.filter(law=law).order_by('chapter_number')
    return render(request, "dashboard/chapter_list.html", {"law": law, "chapters": chapters})

@custom_login_required("dashboard_login")
def chapter_create(request, law_id):
    law = get_object_or_404(LawModel, id=law_id)
    if request.method == "POST":
        chapter_number = request.POST.get("chapter_number")
        title = request.POST.get("title")
        description = request.POST.get("description")
        ChapterModel.objects.create(law=law, chapter_number=chapter_number, title=title, description=description)
        messages.success(request, CREATE)
        return redirect("chapter_list", law_id=law.id)
    return redirect("chapter_list", law_id=law.id)

@custom_login_required("dashboard_login")
def chapter_update(request, law_id, pk):
    law = get_object_or_404(LawModel, id=law_id)
    chapter = get_object_or_404(ChapterModel, id=pk, law=law)
    if request.method == "POST":
        chapter.chapter_number = request.POST.get("chapter_number")
        chapter.title = request.POST.get("title")
        chapter.description = request.POST.get("description")
        chapter.save()
        messages.success(request, UPDATE)
        return redirect("chapter_list", law_id=law.id)
    return redirect("chapter_list", law_id=law.id)

@custom_login_required("dashboard_login")
def chapter_delete(request, law_id, pk):
    chapter = get_object_or_404(ChapterModel, id=pk, law_id=law_id)
    chapter.delete()
    messages.success(request, DELETE)
    return redirect("chapter_list", law_id=law_id)
