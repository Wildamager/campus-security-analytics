import json

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render

from .forms import CameraForm
from .models import Camers, EntryCarLog, EntryPersonLog
from ..data.models import Car, Person

# OpenCV / dlib / TensorFlow are imported lazily inside the handlers below:
# the CV stack is heavy, and importing it at module level would make the whole
# app (and its tests) unusable without a working dlib/TensorFlow build.


@login_required
def camerslist(request):
    camers = Camers.objects.all()
    return render(request, 'dashboard/dashboard.html', {'camers': camers})


@login_required
def addnew_camera(request):
    if request.method == "POST":
        form = CameraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/dashboard/camers/')
    else:
        form = CameraForm()
    return render(request, 'dashboard/add.html', {'form': form})


@login_required
def index(request, id):
    from .tasks import recog

    camera = Camers.objects.get(id=id)
    recog.delay(camera.ip, camera.port, camera.location)
    return render(request, 'dashboard/camerastream.html', {'camera': camera.id})


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'


@login_required
def livecam_feed(request, id):
    from .camera import LiveWebCam

    camera = Camers.objects.get(id=id)
    return StreamingHttpResponse(
        gen(LiveWebCam(camera)),
        content_type='multipart/x-mixed-replace; boundary=frame',
    )


def build_recognition_payload(name, number):
    """Match the last detected person and plate against the database."""
    person = Person.objects.filter(name=name).first()
    car = Car.objects.filter(number=number).first()

    return json.dumps({
        'person': [person.name, person.email, person.contact] if person else ['unknown'] * 3,
        'car': [car.owner, car.number, car.brand] if car else ['unknown', number, 'unknown'],
    })


@login_required
def recognition(request):
    person = EntryPersonLog.objects.order_by('date').last()
    car = EntryCarLog.objects.order_by('date').last()

    payload = build_recognition_payload(
        person.name if person else 'unknown',
        car.number if car else 'unknown',
    )
    return HttpResponse(payload, content_type='application/json')


@login_required
def train(request):
    from .tasks import training

    training.delay()
    return HttpResponse('success')