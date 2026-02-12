"""
URLs pour le module Locations.
"""
from django.urls import path

from locations.views import update_position_view

app_name = "locations"

urlpatterns = [
    path("", update_position_view, name="update"),
]
