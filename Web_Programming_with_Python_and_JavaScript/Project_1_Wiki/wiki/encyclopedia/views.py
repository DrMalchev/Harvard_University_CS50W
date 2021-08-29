from django.http.response import HttpResponse
from django.shortcuts import render

from . import util
import markdown2



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def title(request, title_name):
        return render(request, "encyclopedia/title.html",{
        "title": str (title_name.capitalize()),
        "entry": markdown2.markdown(util.get_entry(title_name))
        
        
})