from django.shortcuts import render
from django.http import Http404

from .models import Board

# Create your views here.

def home(request):
    boards = Board.objects.all()

    return render(request, 'boards/home.html', {'boards': boards})


def board_topics(request, pk):
    try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404 
    return render(request, 'boards/topics.html', {'board': board})
