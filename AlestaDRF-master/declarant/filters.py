from django.db.models import Q
from rest_framework import filters


class CustomSanctionsFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search = request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(code__startswith=search) |
                Q(code=search[:8]) |
                Q(code=search[:6]) |
                Q(code=search[:4]) |
                Q(code=search[:2])
            )
        return queryset