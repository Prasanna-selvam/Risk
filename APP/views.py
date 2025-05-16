from django.shortcuts import render, redirect
from . models import UserPersonalModel
from . forms import UserPersonalForm, UserRegisterForm
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
import numpy as np
import joblib

import serial

ser = serial.Serial()
ser.port = 'COM5'
ser.baudrate = 9600
ser.bytesize = 8
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE

import time
import re

def serialget():
    value=[]
    ser.open()
    time.sleep(1)
    v=b'A'
    ser.write(v)
    while True:
        for line in ser.read():
            if chr(line) != '$':
                value.append(chr(line))
            else:
                print("end")
                ser.close()
                return value


def request(request):
    str1=''
    val=[]
    va=serialget()
    print(va)
    for v in va:
        if(v=='*'):
            continue
        else:  
            if(v!='#'): 
                str1+=v
            else:
                print(str1)
                cleaned_str = re.sub(r'[^0-9.,]', '', str1)
                try:
                    val = [float(num) for num in cleaned_str.split(',')]
                except ValueError:
                    print(f"Error converting {cleaned_str} to float.")
                str1=""
               
    return render(request, '9_Deploy.html', {'val1':int(val[0]),'val2':int(val[1]),'val3':int(val[2]),'val4':int(val[3])})






def Landing_1(request):
    return render(request, '4_Home.html')

def Register_2(request):
    form = UserRegisterForm()
    if request.method =='POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was successfully created. ' + user)
            return redirect('Login_3')

    context = {'form':form}
    return render(request, '2_Register.html', context)


def Login_3(request):
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('Home_4')
        else:
            messages.info(request, 'Username OR Password incorrect')

    context = {}
    return render(request,'3_Login.html', context)

def Home_4(request):
    return render(request, '4_Home.html')

def Teamates_5(request):
    return render(request,'5_Teamates.html')

def Domain_Result_6(request):
    return render(request,'6_Domain_Result.html')

def Problem_Statement_7(request):
    return render(request,'7_Problem_Statement.html')
    

def Per_Info_8(request):
    if request.method == 'POST':
        fieldss = ['firstname','lastname','age','address','phone','city','state','country']
        form = UserPersonalForm(request.POST)
        if form.is_valid():
            print('Saving data in Form')
            form.save()
        return render(request, '4_Home.html', {'form':form})
    else:
        print('Else working')
        form = UserPersonalForm(request.POST)    
        return render(request, '8_Per_Info.html', {'form':form})
    
Model = joblib.load('APP/model.pkl')

def Deploy_9(request): 
    if request.method == "POST":
        int_features = [x for x in request.POST.values()]
        int_features = int_features[1:]
        print(int_features)
        final_features = [np.array(int_features, dtype=float)]
        print(final_features)
        prediction = Model.predict(final_features)
        print(type(prediction))
        output = prediction[0]
        print(f'output{output}')
        if output == 0.0:
            ser.open()
            ser.write(b'C')
            ser.close()
            return render(request, '8_Per_Info.html', {"prediction_text":"THE PATIENT MIGHT NOT GO IN THE STATE OF DANGEROUS ZONE. THIS IS COMPLETELY SAFE ZONE."})
        elif output == 1:
            ser.open()
            ser.write(b'D')
            ser.close()        
            return render(request, '8_Per_Info.html', {"prediction_text":"THE PATIENT MIGHT GO IN THE STATE OF MEDIUM LEVEL ZONE."})
        elif output == 2:
            ser.open()
            ser.write(b'B')
            ser.close()
            return render(request, '8_Per_Info.html', {"prediction_text":"THE PATIENT MIGHT GO IN THE STATE OF DANGEROUS ZONE. WE SHOULD TAKE TREATMENTS TO THIS PATIENT IMMEDIATELY"})
    else:
        return render(request, '9_Deploy.html' )


def Per_Database_10(request):
    models = UserPersonalModel.objects.all()
    return render(request, '10_Per_Database.html', {'models':models})

def Logout(request):
    logout(request)
    return redirect('Login_3')
