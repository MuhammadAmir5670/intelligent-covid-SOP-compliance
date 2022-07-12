from traceback import print_tb
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators import gzip

from manager.utils.camera import Camera
from manager.decorators import make_model

def index(request):
    return render(request, 'manager/stream/index.html', {})


@gzip.gzip_page
@make_model
def web_cam(request, models=[]):
    source = request.GET.get('source', -1)
    return StreamingHttpResponse(Camera(source=source).stream(models), content_type="multipart/x-mixed-replace;boundary=frame")

@gzip.gzip_page
@make_model
def combined(request, models=[]):
    source = request.GET.get('source', -1)
    return StreamingHttpResponse(Camera(source=source).combined(models.pop()), content_type="multipart/x-mixed-replace;boundary=frame")


def validate_source(request):
    source = request.GET.get('source', -1)
    return JsonResponse({'source': Camera.validate_source(source)})