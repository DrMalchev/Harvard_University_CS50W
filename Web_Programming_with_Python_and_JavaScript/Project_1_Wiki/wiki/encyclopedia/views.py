from re import template
from django.http.response import HttpResponse
from django.shortcuts import render

from . import util
from django import forms
import random

import markdown2 # underlined yellow but works fine for me. no action needed.
#models.py
from .models import *
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect



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
 
  

def new(request):
    entries = [entry.lower() for entry in util.list_entries()]
    
    if(request.POST):
        
        data = request.POST.dict()
        title = data.get("qTitle")
        article = data.get("qArticle")
        
        if title not in entries:
            util.save_entry(title,article)
            return HttpResponseRedirect(f"wiki/{title}")
        else:
            return render(request, "encyclopedia/newExists.html", {})
    
        
    else:
        return render(request, "encyclopedia/new.html",{})
    
    
def edit(request, title):
        
        if(request.POST):
            data = request.POST.dict()
            #title = str (title.capitalize())
            article = data.get("qArticle")
            util.save_entry(title,article)

            return HttpResponseRedirect(f"/wiki/{title}")
        
        else:
        
            return render(request, f"encyclopedia/edit.html",{
        "title": title,
        "entry_md": util.get_entry(title)
        #"entry": markdown2.markdown(util.get_entry(title_name))
        })  

def delete(request, title):
    util.delete_entry(title)
    return render(request, "encyclopedia/delete.html", {
                "title": title
        })

def random_page(request):
    entries=util.list_entries()
    rtitle = random.choice(entries)
    return render(request, "encyclopedia/random_page.html",{
        "title": str (rtitle.capitalize()),
        "entry": markdown2.markdown(util.get_entry(rtitle))
        })


