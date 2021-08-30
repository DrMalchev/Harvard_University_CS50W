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
         
    search_key=request.POST.get('q')
    entries = [entry.lower() for entry in util.list_entries()]

    if search_key=="":
        return render(request, "encyclopedia/searchNotFound.html", {
                "search_key": search_key,
        })

    if search_key.lower() in entries:
        return HttpResponseRedirect(f"wiki/{search_key}")
    
    else:
        search_list=[]
        substr_list=[]
        for entry in range(len(entries)):
            if search_key in entries[entry]:
                search_list.append(search_key)
                substr_list.append(entries[entry])
                
            else:
                continue

        substr_len=len(substr_list)

        if substr_len!=0:
            return render(request, "encyclopedia/search.html", {
                "search_key": search_list[0],
                "substring": substr_list,
                "substr_len": substr_len
                
                })
        else:
            return render(request, "encyclopedia/searchNotFound.html", {
            "search_key": search_key
                })
        


     
    
        
