from django.contrib import admin

from .models import PlantingBatch, PlantingSite


class BatchInline(admin.TabularInline):
    model = PlantingBatch
    extra = 0
    readonly_fields = ["batch_code"]
    autocomplete_fields = ["species"]


@admin.register(PlantingSite)
class PlantingSiteAdmin(admin.ModelAdmin):
    list_display = ["name", "kind", "city", "district", "total_trees", "alive_trees", "damaged_trees", "dead_trees", "status", "planting_date", "is_featured"]
    list_filter = ["kind", "status", "city", "is_featured"]
    list_editable = ["alive_trees", "damaged_trees", "dead_trees", "status"]
    search_fields = ["name", "district", "organization"]
    filter_horizontal = ["species"]
    inlines = [BatchInline]
    date_hierarchy = "planting_date"

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PlantingBatch)
class PlantingBatchAdmin(admin.ModelAdmin):
    list_display = ["batch_code", "planting_site", "species", "quantity", "planting_date", "watering_entity"]
    list_filter = ["species", "planting_site__city"]
    search_fields = ["batch_code", "planting_site__name"]
    readonly_fields = ["batch_code"]
    autocomplete_fields = ["planting_site", "species"]
