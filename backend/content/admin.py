from django.contrib import admin

from .models import ArticleCategory, ContentArticle, ContributionGoal, ContributionMethod


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ["icon", "name", "slug", "is_legal", "is_active", "sort_order"]
    list_display_links = ["name"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(ContentArticle)
class ContentArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_published", "needs_legal_review", "published_at"]
    list_filter = ["category", "is_published", "needs_legal_review"]
    search_fields = ["title", "summary", "body"]
    prepopulated_fields = {"slug": ["title"]}
    autocomplete_fields = ["author"]


@admin.register(ContributionMethod)
class ContributionMethodAdmin(admin.ModelAdmin):
    list_display = ["name", "account_information", "is_active", "sort_order"]
    list_editable = ["is_active", "sort_order"]


@admin.register(ContributionGoal)
class ContributionGoalAdmin(admin.ModelAdmin):
    list_display = ["icon", "title", "amount_iqd", "sort_order"]
    list_display_links = ["title"]
