from django.http.response import HttpResponse
from django.shortcuts import render

from . import util

import markdown2 # underlined yellow but works fine for me. no action needed.



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
    
        
        
