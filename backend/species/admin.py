from django.contrib import admin

from .models import TreeSpecies


@admin.register(TreeSpecies)
class TreeSpeciesAdmin(admin.ModelAdmin):
    list_display = ["emoji", "arabic_name", "scientific_name", "heat_tolerance", "drought_tolerance", "water_requirement", "suitable_for_streets", "is_active"]
    list_display_links = ["arabic_name"]
    list_filter = ["is_active", "suitable_for_streets", "suitable_for_farms", "bird_friendly", "fruitful"]
    search_fields = ["arabic_name", "english_name", "scientific_name"]
