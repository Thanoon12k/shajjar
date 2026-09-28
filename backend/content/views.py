from django.shortcuts import get_object_or_404, render

from .models import ArticleCategory, ContentArticle, ContributionGoal, ContributionMethod


def article_list(request):
    cat = request.GET.get("c")
    qs = ContentArticle.published.select_related("category").filter(category__is_legal=False)
    if cat:
        qs = qs.filter(category__slug=cat)
    cats = ArticleCategory.objects.filter(is_active=True, is_legal=False)
    return render(request, "content/list.html", {"articles": qs, "cats": cats, "current": cat})


def law(request):
    cats = ArticleCategory.objects.filter(is_active=True, is_legal=True).prefetch_related("articles")
    return render(request, "content/law.html", {"cats": cats})


def article(request, slug):
    a = get_object_or_404(ContentArticle.published.select_related("category", "author"), slug=slug)
    related = ContentArticle.published.filter(category=a.category).exclude(pk=a.pk)[:3]
    return render(request, "content/article.html", {"a": a, "related": related})


def contribute(request):
    return render(
        request,
        "content/contribute.html",
        {"methods": ContributionMethod.objects.filter(is_active=True), "goals": ContributionGoal.objects.all()},
    )
