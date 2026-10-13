from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Note
from .serializers import NoteSerializer


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def note_list_create(request):

    if request.method == "GET":
        notes = Note.objects.all().order_by("-created_at")
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    serializer = NoteSerializer(data=request.data)

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


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def note_detail(request, pk):

    note = get_object_or_404(Note, pk=pk)

    
    if request.method == "GET":
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    elif request.method == "PUT":
        serializer = NoteSerializer(note, data=request.data)

    # PATCH: Update selected fields
    elif request.method == "PATCH":
        serializer = NoteSerializer(
            note,
            data=request.data,
            partial=True
        )

    
    else:
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

