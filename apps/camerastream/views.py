from django.shortcuts import render, redirect
from django.http.response import StreamingHttpResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from .camera import LiveWebCam
from .models import Camers, EntryCarLog, EntryPersonLog
from .forms import CameraForm
from .DetectionsNumbers import main
from ..data.models import Person, Car
import time
from .tasks import recog, training
import json


@login_required
def camerslist(request):
    camers = Camers.objects.all()
    # recognition.delay()
    return render(request, 'dashboard/dashboard.html', {'camers':camers})

@login_required
def addnew_camera(request):  
    if request.method == "POST":  
        form = CameraForm(request.POST)  
        if form.is_valid():  
            form.save()  
            return redirect('/dashboard/camers/')  
    else:  
        form = CameraForm()
    return render(request,'dashboard/add.html',{'form':form}) 

@login_required
def index(request, id):
    camera = Camers.objects.filter(id=id)
    recog.delay(camera[0].ip, camera[0].port, camera[0].location)
    return render(request, 'dashboard/camerastream.html', {'camera':camera[0].id})

def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@login_required
def webcam_feed(request, id):
    
    camera = Camers.objects.get(id=id)
    return StreamingHttpResponse(gen(IPWebCam(camera)),
					content_type='multipart/x-mixed-replace; boundary=frame')

def test(name, number):
    person_exists = Person.objects.filter(name=name).exists()
    car_exists = Car.objects.filter(number=number).exists()
    person = Person.objects.filter(name=name).first()
    car = Car.objects.filter(number=number).first()

    result = {
        'person': [person.name, person.email, person.contact] if person else ['unknown', 'unknown', 'unknown'],
        'car': [car.owner, car.number, car.brand] if car else ['unknown', number, 'unknown'],
    }
    return json.dumps(result)


@login_required
def recognition(request):
    person = EntryPersonLog.objects.order_by('date').last()
    car = EntryCarLog.objects.order_by('date').last()
    person_name = person.name if person else 'unknown'
    car_number = car.number if car else 'unknown'
    return HttpResponse(test(person_name, car_number), content_type='application/json')


@login_required
def webcam_feed(request, id):
    camera = Camers.objects.get(id=id)
    return StreamingHttpResponse(gen(LiveWebCam(camera)),
					content_type='multipart/x-mixed-replace; boundary=frame')

def train(request):
    training.delay()
    return HttpResponse('succes')
