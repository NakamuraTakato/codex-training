from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from taggit.models import Tag

from .forms import BootstrapAuthenticationForm, PostForm, SignUpForm
from .models import Category, Post


class HomeView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):  # type: ignore[override]
        queryset = Post.objects.published().select_related("author", "category").prefetch_related("tags")
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(category__name__icontains=query)
                | Q(tags__name__icontains=query)
            ).distinct()
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        tag_slug = self.request.GET.get("tag")
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["categories"] = (
            Category.objects.annotate(
                post_count=Count("posts", filter=Q(posts__status=Post.Status.PUBLISHED))
            ).order_by("name")
        )
        context["tags"] = (
            Tag.objects.annotate(
                post_count=Count(
                    "taggit_taggeditem_items",
                    filter=Q(taggit_taggeditem_items__content_object__status=Post.Status.PUBLISHED),
                )
            ).order_by("name")
        )
        context["query"] = self.request.GET.get("q", "")
        filters = self.request.GET.copy()
        filters.pop("page", None)
        context["filters"] = filters.urlencode()
        category_filters = filters.copy()
        if "category" in category_filters:
            del category_filters["category"]
        tag_filters = filters.copy()
        if "tag" in tag_filters:
            del tag_filters["tag"]
        context["category_filters"] = category_filters
        context["tag_filters"] = tag_filters
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_field = "slug"

    def get_queryset(self):  # type: ignore[override]
        queryset = Post.objects.select_related("author", "category").prefetch_related("tags")
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status=Post.Status.PUBLISHED)
        return queryset


class CategoryDetailView(ListView):
    model = Post
    template_name = "blog/category_detail.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):  # type: ignore[override]
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])  # type: ignore[attr-defined]
        return (
            Post.objects.published()
            .filter(category=self.category)
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["category"] = self.category  # type: ignore[attr-defined]
        return context


class TagDetailView(ListView):
    model = Post
    template_name = "blog/tag_detail.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):  # type: ignore[override]
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])  # type: ignore[attr-defined]
        return (
            Post.objects.published()
            .filter(tags__in=[self.tag])
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag  # type: ignore[attr-defined]
        return context


class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):  # type: ignore[override]
        post = self.get_object()  # type: ignore[attr-defined]
        return post.author == self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):  # type: ignore[override]
        form.instance.author = self.request.user
        messages.success(self.request, "投稿を作成しました。")
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    slug_field = "slug"

    def form_valid(self, form):  # type: ignore[override]
        messages.success(self.request, "投稿を更新しました。")
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    slug_field = "slug"
    success_url = reverse_lazy("dashboard")

    def delete(self, request: HttpRequest, *args, **kwargs):  # type: ignore[override]
        messages.success(request, "投稿を削除しました。")
        return super().delete(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/dashboard.html"
    context_object_name = "posts"

    def get_queryset(self):  # type: ignore[override]
        return (
            Post.objects.filter(author=self.request.user)
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-updated_at")
        )


def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "アカウントを作成しました。")
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = BootstrapAuthenticationForm

    def form_valid(self, form):  # type: ignore[override]
        messages.success(self.request, "ログインしました。")
        return super().form_valid(form)
