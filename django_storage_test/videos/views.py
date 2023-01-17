from django.shortcuts import render


def upload_form(request):
    return render(request, "upload_form.html")
