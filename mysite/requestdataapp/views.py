from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
import os

from .forms import UserBioForm, UploadFileForm


def process_get_view(request:HttpRequest) -> HttpResponse:

    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    try:
        result = int(a) + int(b)
    except:
        result = a + b
        pass
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    
    return render(request, "requestdataapp/request-query-params.html", context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm()
    }
    return render(request, "requestdataapp/user-bio-form.html", context=context)


def handle_file_upload(request: HttpRequest) -> HttpResponse:

    # if not request.POST.get('file_save'):
    #     file_save = False
    file_save = request.POST.get('file_save')
    file_save_error = request.POST.get('file_save_error')
    print(request.POST.get('file_save'))
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data['file']

            # myfile = request.FILES["myfile"]
            filesize = myfile.size
            if filesize <= 2 ** 20:
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                print("saved file", filename)
                file_save = True
                file_save_error = False
        else:
            file_save = True
            file_save_error = True
    else:
        form = UploadFileForm()

    context = {
        "file_save": file_save,
        "file_save_error": file_save_error,
        "form": form,
        }
    return render(request, "requestdataapp/file-upload.html", context=context)

