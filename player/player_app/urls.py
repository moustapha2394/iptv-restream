from django.urls import path
from django.shortcuts import render

def watch_view(request):
    return render(request, 'watch.html')

urlpatterns = [
    path('', watch_view, name='watch'),
    path('watch/', watch_view, name='watch_alt'),
]
