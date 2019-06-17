from django.http import HttpResponse


def home_page(request):
    return HttpResponse("<html><title>To-Do List</title></html>")
