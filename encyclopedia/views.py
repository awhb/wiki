from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
import markdown2
from . import util
import secrets

class EntryForm(forms.Form):
    title = forms.CharField(label="Title:", widget=forms.TextInput(attrs={'class': 'form-control col-md-8 col-lg-8'}))
    body = forms.CharField(label="Body:", widget=forms.Textarea(attrs={'class': 'form-control col-md-8 col-lg-8', 'rows': 10}))
    edit = forms.BooleanField(initial=False, required=False, widget=forms.HiddenInput())

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    # if invalid entry load error page
    if util.get_entry(title) is None: 
        return render(request, "encyclopedia/error.html", {
            "title": title
        })
    # if valid entry load page with relevant entry
    else: 
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "contents": markdown2.markdown(util.get_entry(title))
        })

def search(request):
    # Take in the data the user submitted and save it as form
    title = request.GET.get('q', '')
    # Check if form data is valid (server-side)
    # if entry is found redirect to site
    if util.get_entry(title) is not None: 
        return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))

    else: 
        # Initialise something 
        matches = []
        for entry in util.list_entries():
            if title.upper() in entry.upper():
                matches.append(entry)
        # load up the search results page
        return render(request, "encyclopedia/search.html", {
            "title": title,
            "matches": matches
        })

def create(request): 
    # handle POST request:
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = EntryForm(request.POST)
        # Check if form data is valid (server-side)
        if form.is_valid():
            # Initialise variables from cleaned data
            title = form.cleaned_data["title"]
            body = form.cleaned_data["body"]
            edit = form.cleaned_data["edit"]

            if util.get_entry(title) is None or edit is True: 
                util.save_entry(title, body)
                return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))
            else: 
                return render(request, "encyclopedia/create.html", {
                    "createform": EntryForm(),
                    "existing": True,
                    "entry": title})
                
    # handle GET request
    else: 
        return render(request, "encyclopedia/create.html", {
            "createform": EntryForm(),
            "existing": False
        })


def edit(request, title):
    # if invalid entry load error page
    if util.get_entry(title) is None: 
        return render(request, "encyclopedia/error.html", {
        "title": title
        })
    else: 
        # modify the initial entry form to suit current context
        editform = EntryForm()
        editform.fields["title"].initial = title
        editform.fields["title"].widget = forms.HiddenInput()
        editform.fields["body"].initial = util.get_entry(title)
        editform.fields["edit"].initial = True
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "editform": editform
        })

def random(request): 
    all_entries = util.list_entries()
    random_entry = secrets.choice(all_entries)
    return HttpResponseRedirect(reverse("entry", kwargs={"title": random_entry}))
