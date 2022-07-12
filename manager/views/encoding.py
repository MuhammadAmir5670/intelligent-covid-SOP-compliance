from django.shortcuts import redirect, render

from django.contrib import messages
from manager.models import Encoding

def activate(request, id):
    encoding = Encoding.objects.get(pk=id)
    encoding.active = True
    encoding.save()
    messages.success(request, 'Encoding Activated Successfully')
    return redirect(encoding.student)


def deactivate(request, id):
    encoding = Encoding.objects.get(pk=id)
    encoding.active = False
    encoding.save()
    messages.success(request, 'Encoding Deactivated Successfully')
    return redirect(encoding.student)


def delete(request, id):
    encoding = Encoding.objects.get(pk=id)
    encoding.delete()
    messages.success(request, 'Encoding Deleted Successfully')
    return redirect(encoding.student)