from __future__ import annotations

from django.urls import path

from .views import (
    CategoryDetailView,
    CustomLoginView,
    DashboardView,
    HomeView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostUpdateView,
    TagDetailView,
    signup,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("signup/", signup, name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("post/new/", PostCreateView.as_view(), name="post_create"),
    path("post/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("post/<slug:slug>/edit/", PostUpdateView.as_view(), name="post_update"),
    path("post/<slug:slug>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category_detail"),
    path("tag/<slug:slug>/", TagDetailView.as_view(), name="tag_detail"),
]
