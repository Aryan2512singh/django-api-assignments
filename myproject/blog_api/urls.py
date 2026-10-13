
from django.urls import path
from .views import (
    AuthorListCreateView,
    AuthorDetailView,
    AuthorPostsView,
    PostListCreateView,
    PostDetailView,
    PostCommentsView,
    CommentDetailView,
)

urlpatterns = [
    path("authors/", AuthorListCreateView.as_view(), name="author-list"),
    path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author-detail"),
    path("authors/<int:pk>/posts/", AuthorPostsView.as_view(), name="author-posts"),

    path("posts/", PostListCreateView.as_view(), name="post-list"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:pk>/comments/", PostCommentsView.as_view(), name="post-comments"),

    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
]
