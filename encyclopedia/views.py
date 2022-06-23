from audioop import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from markdown2 import Markdown
from django import forms
import random


from . import util

entries = util.list_entries()


class CreateForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(
        attrs={"class": "title", "placeholder": "Enter a title", "style": "width: 80%; margin-bottom: 10px"}))
    content = forms.CharField(label="", widget=forms.Textarea(
        attrs={"class": "content", "rows": 3, "cols": 5, "style": "width: 80%; height: 50vh"}))

class EditForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea(
        attrs={"rows": 3, "cols": 5, "style": "width: 80%; height: 50vh"}))

def index(request):
    print(util.list_entries())
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def get_title(request, title):
    content = util.get_entry(title)

    content_converted = Markdown().convert(content)

    if title not in entries:
        return render(request, 'encyclopedia/error.html', {
            'error': "No topic exits",
        })

    return render(request, "encyclopedia/title.html", {
        "content": content_converted,
        "title": title,
    })


def search(request):
    query = request.GET.get('q', '')
    if query is None or query == '':
        return render(request, "encyclopedia/search.html")

    for entry in entries:
        if query == entry:
            return get_title(request, entry)

    closest = [entry for entry in entries if query in entry or query.lower()
               in entry.lower()]

    return render(request, "encyclopedia/search.html", {
        "closest": closest
    })


def create(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            if util.get_entry(title):
                return render(request, "encyclopedia/create.html", {
                    "error": "This title has exits. You can try to edit it manually",
                    "form": form
                })
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("index"))

    return render(request, "encyclopedia/create.html", {
        "form": CreateForm()
    })

def edit(request, title):
    if request.method == "GET":
        content = util.get_entry(title)

        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": EditForm(initial={"text": content})
        })
    elif request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['text']
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("index"))

def random_title(request):
    title = random.choice(entries)
    content = util.get_entry(title)
    content_convert = Markdown().convert(content)

    return render(request, "encyclopedia/title.html", {
        "title": title,
        "content": content_convert
    })


        