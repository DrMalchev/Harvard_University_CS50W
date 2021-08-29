from re import template
from django.http.response import HttpResponse
from django.shortcuts import render

from . import util

import markdown2 # underlined yellow but works fine for me. no action needed.
#models.py
from .models import *
from django.http.response import HttpResponseRedirect


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def title(request, title_name):
    if util.get_entry(title_name)!=None:
    
        return render(request, "encyclopedia/title.html",{
        "title": str (title_name.capitalize()),
        "entry": markdown2.markdown(util.get_entry(title_name))
        })
    else:
        return render(request, "encyclopedia/notFound.html", {
        "entries": util.list_entries()
    })
    
def search(request):
    #if request.method == "GET":
        
    
    search_key=request.POST.get('q')
    return HttpResponseRedirect(f"wiki/{search_key}")
    #entries = [x.lower() for x in util.list_entries()]
    #find_entries = list()

    #search_key = request.POST.get('q',"")
    #return render(request, "encyclopedia/search.html", {"no_result": f"No results for {search_key}"})
        

    #if search_key.lower() in entries:
        #return HttpResponseRedirect(f"wiki/{search_key}")
    #return HttpResponseRedirect("wiki/css")
        
    """ for entry in entries:
        if search_box in entry:
            find_entries.append(entry)
        else:
            print(f'{find_entries}')
    if find_entries:
        return render(request, "encyclopedia/search.html", {
          "search_result": find_entries,
          "search": search_box
    })
    else:
        return render(request, "encyclopedia/search.html", {"no_result": f"No results for {search_box}"}) """
        
