from django.urls import path

from .views import (
    DefectListView,
    EstimateView,
    ModelListView,
    SeriesListView,
    StorageListView,
)

urlpatterns = [
    path("series/",                      SeriesListView.as_view(),  name="api-series"),
    path("models/<int:series_id>/",      ModelListView.as_view(),   name="api-models"),
    path("storage/<int:model_id>/",      StorageListView.as_view(), name="api-storage"),
    path("defects/",                     DefectListView.as_view(),  name="api-defects"),
    path("estimate/",                    EstimateView.as_view(),    name="api-estimate"),
]
