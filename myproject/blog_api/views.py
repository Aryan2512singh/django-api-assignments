from django.shortcuts import render

from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .models import Author, Post, Comment
from .serializers import (AuthorSerializer, PostListSerializer, PostDetailSerializer, PostWriteSerializer,CommentSerializer,)


class AuthorListCreateView(APIView):

    def get(self, request):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AuthorSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class AuthorDetailView(APIView):

    def get(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)



class PostListCreateView(APIView):

    def get(self, request):
        posts = Post.objects.select_related("author").all().order_by("-id")

        
        search = request.query_params.get("search")
        if search:
            posts = posts.filter(title__icontains=search)

        
        author_id = request.query_params.get("author")
        if author_id:
            posts = posts.filter(author_id=author_id)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(posts, request)

        serializer = PostListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PostWriteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class PostDetailView(APIView):

    def get(self, request, pk):
        post = get_object_or_404(
            Post.objects.select_related("author").prefetch_related("comments"),
            pk=pk
        )
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostWriteSerializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostWriteSerializer(
            post,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class PostCommentsView(APIView):

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        comments = post.comments.all().order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(post=post)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CommentDetailView(APIView):

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthorPostsView(APIView):

    def get(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        posts = author.posts.select_related("author").order_by("-id")
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

