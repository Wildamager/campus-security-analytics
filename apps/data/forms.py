from django import forms  
from .models import Person, Car
class PersonForm(forms.ModelForm):  
    class Meta:  
        model = Person  
        fields = ['name', 'contact', 'email', 'image'] #https://docs.djangoproject.com/en/3.0/ref/forms/widgets/
        widgets = { 'name': forms.TextInput(attrs={ 'class': 'form-control' }), 
            'email': forms.EmailInput(attrs={ 'class': 'form-control' }),
            'contact': forms.TextInput(attrs={ 'class': 'form-control' }),
            'image': forms.FileInput(),
        }


class CarForm(forms.ModelForm):  
    class Meta:  
        model = Car  
        fields = ['owner', 'number', 'brand'] #https://docs.djangoproject.com/en/3.0/ref/forms/widgets/
        widgets = { 'owner': forms.TextInput(attrs={ 'class': 'form-control' }), 
            'number': forms.TextInput(attrs={ 'class': 'form-control' }),
            'brand': forms.TextInput(attrs={ 'class': 'form-control' }),
        }
