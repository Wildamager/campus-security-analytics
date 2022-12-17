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
            try:  
                form.save() 
                print('i') 
                return redirect('/dashboard/camers/')  
            except:  
                print('ere')
                pass 
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
    print(name)
    print(Person.objects.filter(name=name).exists())
    print(Car.objects.filter(number=number))
    if Person.objects.filter(name=name).exists() and Car.objects.filter(number=number).exists():
        print('OPEN THE DOOR AND BARRIER')
        person = Person.objects.get(name=name)
        car = Car.objects.get(number=number)
        result={
            'person':[person.name, person.email, person.contact],
            'car':[car.owner, car.number, car.brand]
        }
    elif (Person.objects.filter(name=name).exists()==True)and(Car.objects.filter(number=number).exists()==False):
        print('OPEN THE DOOR')
        person = Person.objects.get(name=name)
        result={
            'person':[person.name, person.email, person.contact], 
            'car':['unknown', number, 'unknown']
        }
    elif (Person.objects.filter(name=name).exists()==False)and(Car.objects.filter(number=number).exists()==True):
        rint('OPEN THE BARRIER')
        car = Car.objects.get(number=number)
        result={
            'person':[name, 'unknown', 'unknown'],
            'car':[car.owner, car.number, car.brand]
        }
    else:
        result={
            'person':[name, 'unknown', 'unknown'],
            'car':['unknown', number, 'unknown']
        }
    result = json.dumps(result)
    yield (result)


@login_required
def recognition(request):
    print(len(EntryPersonLog.objects.all()))
    if len(EntryPersonLog.objects.all())==0:
        car = EntryCarLog.objects.latest('date')
        person='unknown'
        return StreamingHttpResponse(test(person, car.number))
    elif len(EntryCarLog.objects.all())==0:
        person = EntryPersonLog.objects.latest('date')
        car='unknown'
        return StreamingHttpResponse(test(person.name, car))
    elif (len(EntryCarLog.objects.all())!=0) and (len(EntryPersonLog.objects.all())!=0):
        person = EntryPersonLog.objects.latest('date')
        car = EntryCarLog.objects.latest('date')
        return StreamingHttpResponse(test(person.name, car.number))
    else:
        person='unknown'
        car='unknown'
        return StreamingHttpResponse(test(person, car))


@login_required
def livecam_feed(request, id):
    camera = Camers.objects.get(id=id)
    return StreamingHttpResponse(gen(LiveWebCam(camera)),
					content_type='multipart/x-mixed-replace; boundary=frame')

def train(request):
    training.delay()
    return HttpResponse('succes')
