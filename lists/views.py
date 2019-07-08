from django.shortcuts import redirect, render
from lists.models import List
from lists.forms import ItemForm, ExistingListItemForm, NewListForm
from django.contrib.auth import get_user_model

User = get_user_model()


def home_page(request):
    return render(request, "lists/home.html", {"form": ItemForm()})


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)
    if request.method == "POST":
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)
    return render(request, "lists/list.html", {"list": list_, "form": form})


def new_list(request):
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(str(list_))
    return render(request, "lists/home.html", {"form": form})


def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, "lists/my_lists.html", {"owner": owner})
