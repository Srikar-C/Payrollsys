from django.shortcuts import render,redirect
import requests
import json
from django.http import JsonResponse,HttpResponse
import random
from django.core.mail import send_mail
from datetime import datetime
from .models import Registration
from payroll import settings
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def login(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        usertype=request.POST.get('role')
        data={
            "username":username,
            "password":password,
            "usertype":usertype
        }
        print(username,password,usertype)
        flask_url="http://192.168.0.5:5000/login"
        response=requests.post(flask_url,json=data)
        if response.status_code == 200:
            flask_url_responsedata=response.json()
            print(flask_url_responsedata)
            if flask_url_responsedata['status']=="success":
                request.session['Authenticated'] = True
                request.session['username'] = flask_url_responsedata['username']
                request.session['user_id'] = flask_url_responsedata['user_id']
                request.session['user_email']=flask_url_responsedata['employee_email']
                request.session['user_type']=flask_url_responsedata['user_type']
                if flask_url_responsedata['user_type']=="Employer":
                    Employee_Count=flask_url_responsedata['Total_employees'][0]['COUNT(Employee_id)']
                    All_Names_Ids=flask_url_responsedata['all_employee_name_id']
                    print(All_Names_Ids)
                    return render(request,'Admin/opening.html',{"status":flask_url_responsedata,"username":flask_url_responsedata['username']
                                                         ,'email':flask_url_responsedata['employee_email'],'user_id':flask_url_responsedata['user_id'],
                                                         'user_type':flask_url_responsedata['user_type'],"Employee_Count":Employee_Count,
                                                         "All_Names_Ids":All_Names_Ids})
                
                elif flask_url_responsedata['user_type']=="Employee":
                    return render(request,'user/clock.html',{"status":flask_url_responsedata,"username":flask_url_responsedata['username'],'email':flask_url_responsedata['employee_email']
                                                        ,'user_id':flask_url_responsedata['user_id'],'user_type':flask_url_responsedata['user_type'],"clock_in_time":flask_url_responsedata['clock_in_time']
                                                        ,"announcement_info":flask_url_responsedata['announcement_info'],"date_of_births":flask_url_responsedata['date_of_births'],"holiday_info":flask_url_responsedata['holiday_info'],"leaves_info":flask_url_responsedata['leaves_info']})
               
            else:
                print("status code",response.status_code)
                return render(request,'login.html',{"failed":"login credentials are wrong"})
    return render(request,'login.html')



def register(request):
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']
        email=request.POST['email']
        usertype=request.POST.get('role')
        confpass=request.POST['confpass']
        print(username,email,usertype,password,confpass)
        # user=Registration(username=name,password=password,Email=email,UserType=role)
        # user.save()
        data={
            "username":name,
            "email":email,
            "usertype":role,
            "password":password
        }
        flask_url="http://192.168.0.5:5000/data_receive"
        response=requests.post(flask_url,json=data)
        if response.status_code==200:
            flask_response_data=response.json()
            print(flask_response_data)
            print("data sent successfuly")
        else:
            print("failed",response.status_code)
    return render(request,'register.html')

def forgot_password(request):
    return render(request,'forgot.html')

def home(request):
    if request.session.get('Authenticate'):
        username = request.session['username']
        return render(request, 'user/clock.html', {'username': username})
    else:
        return redirect('login')
    
def logout(request):
    request.session.clear()
    return redirect('login')

def forgot(request):
    return render(request,'forgot_password.html')

def forgot_password(request):
    global OtpNumber
    global Forgot_UserData
    global Forgot_UserName
    global email
    email=""
    if request.method == 'POST':
        email=request.POST['email']
        try:
            data={
            "email":email
            }
            print(data)
            flask_url="http://192.168.0.5:5000/validate_email"
            response=requests.post(flask_url,json=data)
            flask_response=response.json()
            print(flask_response['status'])
            if flask_response['status']:
                validate_password(request,"otpenter",email)
            else:
                print("error coming",response.status_code)
        except Exception as e:
            print("error is occures")
    if email:
        return render(request,'forgot.html',{"email":email,"name":"sudhakar"})
    return render(request,'forgot.html')

def validate_password(request,keyword,email):
    global OtpNumber
    if keyword=='otpenter':
        print("successs")
        OtpNumber=random.randint(100000,999999)
        subject = 'Email with Template'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['vamsit186@gmail.com',]
        message=" your request to change password is accepted \n Your 6 digit otp is"+str(OtpNumber)
        print("upto this")
        send_mail(subject, message, from_email, recipient_list)
        print("upto this",email)

    if keyword=="otpvalidate":
        if request.method == 'POST':
            otp = request.POST.get('input1')
            new_password = request.POST.get('input2')
            confirm_password = request.POST.get('input3')
            email = request.POST.get('email')
            print(otp,email)
            data={
                'email':email,
                'password':new_password
            }

            if(OtpNumber==int(otp)):
                flask_url="http://192.168.0.5:5000/update_password"
                response=requests.post(flask_url,json=data)
                flask_response=response.json()
                if(response.status_code==200):
                  print(flask_response)
                else:
                    print(response.status_code)
                print("otp verification completed")
                return render(request,'login.html')
            else:
                print("this is ok")
    return render(request,'forgot.html',{"name":"sudhakar"})


def clock(request,username,user_type,email,user_id):
    flask_url="http://192.168.0.5:5000/get_clock_in"
    data={
        "employee_id":user_id
    }
    response=requests.post(flask_url,json=data)
    print("response is",response.json())
    response_data=response.json()
    print(response_data)
    if response_data['status']=="Success":
        print()
        return render(request,'user/clock.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,"current_time":response_data['current_time']})
    else:
        return render(request,'user/clock.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})

def attendance_data(request,username,user_type,email,user_id):
    start = request.POST.get('start_date')
    end = request.POST.get('end_date')

    
    data={
        "request_type":"all_data",
        "username":username,
        "id":user_id,
        "start_date":start,
        "end_date":end,
    }
    flask_url="http://192.168.0.5:5000/get_attendance_data"
    response=requests.post(flask_url,json=data)
    if response.status_code==200:
        response_data=response.json()
        print("response data is",response_data)
        return render(request,'user/clock.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})
    else:
        print("data not going")
    
    return render(request,'user/clock.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})

def get_specific_data(request,username,user_type,email,user_id):
    print("print getsepcific function calling")
    if request.method=="POST":
        start_date=request.POST.get('start_date')
        end_date=request.POST.get('end_date')
        print("dates are",start_date,end_date)
        # start_date=datetime.strptime(start_date,"%Y-%m-%d").date()
        # end_date=datetime.strptime(end_date,"%Y-%m-%d").date()
        data={
            "start_date":start_date,
            "end_date":end_date,
            "username":username,
            "id":user_id,
            "request_type":"between_dates"
        }
        flask_url="http://192.168.0.5:5000/get_attendance_data"
        response=requests.post(flask_url,json=data)
        if response.status_code==200:
            print("getting data",response.json())
            return render(request,'user/clock.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})

        else:
            print("data is not going",response.status_code)
    return render(request,'user/clock.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})  

def status(request):
    if request.method=='POST':
        completed_tasks=request.POST.get('completed')
        issues=request.POST.get('issues')
        print(completed_tasks,issues)
        feature_targets=request.POST['targets']
        status_update=request.POST['status']
        empid="123"
        empname="sudha"
        # empid=request.POST.get('empid')
        # empname=request.POST.get('empname')
        print('------------------',completed_tasks)
        print('------------------',issues)
        print('------------------',feature_targets,status_update)
       

        if issues is None:
            issues='No Issues'
   
        data={
            'employeeid':empid,
            'employeename':empname,
            'email':request.session['email'],
            'completed':completed_tasks,
            'issues':issues,
            'upcoming':feature_targets,
            'statusUpdate':status_update
        }
        flask_url="http://192.168.0.5:5000/status_update_data"
        response=requests.post(flask_url,json=data)
        flask_response=response.json()
        print(flask_response)
    else:
        print('Failed to fetch location details. Status Code:')
    return render(request,'user/status.html')

def statusCheck(request):
    if request.method=='POST':
        # empid=request.POST.get('empid')
        # empname=request.POST.get('empname')
        empid="123"
        empname="sudha"
        date=request.POST['select_date']
        print('------------------',empid)
        print('------------------',empname)
        print('------------------',date)
        data={
            'employeeid':empid,
            'employeename':empname,
            'start_date':date,
            "end_date":"2024-02-25",
             "request_type":"single_date"
        }
        flask_url="http://192.168.0.5:5000/get_status_update_data"
        response=requests.post(flask_url,json=data)
        if response.status_code==200:
            flask_response=response.json()
            status_update=flask_response['status_update']
            print(flask_response)
            return render(request,'user/status.html',{"status_update":status_update})
            
        else:
            print("error",response.status_code)
    else:
        print('Failed to fetch location details. Status Code:')
    return render(request,'status.html')

def get_Status_Data(request):
    if request.method=='POST':
        start_date=request.POST['start_date']
        end_date=request.POST['end_date']
        print("start-date end_date",start_date,end_date)
        data={
            "start_date":start_date,
            "end_date":end_date,
            "employeeid":"123",
            "request_type":"in_between_dates"
        }
        flask_url="http://192.168.0.5:5000/get_status_update_data"
        response=requests.post(flask_url,json=data)
        if response.status_code==200:
            response_date=response.json()
            print(response)
            total_status_data=response_date['request_data']
            print(total_status_data)
            return render(request,'user/status.html',{"total_data":total_status_data})
            print("data is going")
        else:
            print("data is not going",response.status_code)
    return render(request,'status.html')

def update_Status(request):
    pass




def update_location(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        username = request.POST.get('username')
        email= request.POST.get ('email')
        buttonname=request.POST.get('buttonname')
        id = request.POST.get('userid')
        print("button name",request.POST.get('buttonname'))
        print(username,email,"userid-",id)
        url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}'

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(data)
            if 'error' not in data:
                address = data.get('address', {})
                historic = data.get('display_name', 'Address not found')
                county = address.get('county', 'County not found')
                print('-----------------',historic)
                print('-------------------',county)
                data={
                        'employee_id':id,
                        'employee_name':username,
                        'historic':historic,
                        'district':county,
                        'button_name':buttonname
                    }
                print("data that I am sending is ",data)
                flask_url="http://192.168.0.5:5000/clock_in"
                response=requests.post(flask_url,json=data)
                flask_response=response.json()
                print("clock and clockout response is",flask_response)
                print(flask_response)
                if flask_response['status']=="success":
                    print("this is the response data",flask_response)
                    print("clock in success")
                    input_date = datetime.strptime(flask_response['current_time'], "%a, %d %b %Y %H:%M:%S %Z")
                    current_time = input_date.strftime("%H-%M-%S")
                    response_data={
                        "message":"success",
                        "current_time":current_time
                    }
                    print(response_data)
                    print("current time if:",current_time)
                    return JsonResponse(response_data)
                else:
                    print("this is clock out")
                    # print("current time else:",Clock_In_Time)
                    print("clock out response",response.status_code)
                    try:
                        print("upto this executed................")
                        current_time_str = flask_response['current_time']
                        Clock_In_Time = datetime.strptime(current_time_str, "%H:%M:%S")
                        print("Clock In Time:", Clock_In_Time)
                        # Clock_In_Time = datetime.strptime(flask_response['current_time'], "%a, %d %b %Y %H:%M:%S %Z")
                        # print(Clock_In_Time)
                        avg_working_hrs = Clock_In_Time.strftime("%H-%M-%S")
                        
                        response_data={
                            "message":"success",
                            "current_time":avg_working_hrs }
                        
                        # return JsonResponse(response_data)
                        print("clock in time in try block",avg_working_hrs)
                        return render(request, 'user/clock.html',{"current_time":avg_working_hrs})
                    
                    except:
                        print("already clockin person pressing clock in again")
                    
                    
                    #return render(request, 'sample.html', {"username":"varun"})
            else:
                print('Failed to fetch location details.')
        else:
            print('Failed to fetch location details. Status Code:', response.status_code)
        
    return render(request, 'user/clock.html',{"current_time":avg_working_hrs})



def accept(request,username,user_type,email,user_id):
    data={
        "employee_id":user_id,
        "request_type":"accept"
    }
    flask_url="http://192.168.0.5:5000/accepted_leave_history"
    response=requests.post(flask_url,json=data)
    if response.status_code==200:
        response_data=response.json()
        try:
            accepted_data=response_data['Employee_Leave_history']

            for i in range(len(accepted_data)):
                input_date = datetime.strptime(accepted_data[i]['Start_date'], "%a, %d %b %Y %H:%M:%S %Z")
                start_date = input_date.strftime("%Y-%m-%d")
                input_date = datetime.strptime(accepted_data[i]['End_date'], "%a, %d %b %Y %H:%M:%S %Z")
                end_date = input_date.strftime("%Y-%m-%d")
                accepted_data[i]['Start_date']=start_date
                accepted_data[i]['End_date']=end_date
            return render(request,'user/accept.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,'accepted_data':accepted_data})
        except:
            print("data is not coming")
    else:
        print("data is not going",response.status_code)
    return render(request,'user/accept.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})
def pending(request,username,user_type,email,user_id):
    data={
        "employee_id":user_id,
        "request_type":"pending"
    }
    flask_url="http://192.168.0.5:5000/accepted_leave_history"
    response=requests.post(flask_url,json=data)
    print(response)
    if response.status_code==200:
        response_data=response.json()
        # print('-----------------------------------Pending--------------------------------------------------------')
        # print(accepted_data)
        try:
            accepted_data=response_data['Employee_Leave_history']
            print("this is accepted data",accepted_data)
            for i in range(len(accepted_data)):
                
                # input_date = datetime.strptime(accepted_data[i]['Start_date'], "%a, %d %b %Y %H:%M:%S %Z")
                # start_date = input_date.strftime("%Y-%m-%d")
                start_date = date_convertion( accepted_data[i]['Start_date'] )
                input_date = datetime.strptime(accepted_data[i]['End_date'], "%a, %d %b %Y %H:%M:%S %Z")
                end_date = input_date.strftime("%Y-%m-%d")
                accepted_data[i]['Start_date']=start_date
                accepted_data[i]['End_date']=end_date
                print(accepted_data[i]['End_date'])
                
            return render(request,'user/pending.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,'accepted_data':accepted_data})
        except:
            print("data is not coming")
    else:
        print("data is not going",response.status_code)
    return render(request,'user/pending.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})

def reject(request,username,user_type,email,user_id):
    print("all details",username,user_id,email,user_type)
    data={
        "employee_id":user_id,
        "request_type":"reject"
    }
    flask_url="http://192.168.0.5:5000/accepted_leave_history"
    response=requests.post(flask_url,json=data)
    print(response)
    if response.status_code==200:
        response_data=response.json()
        try:
            accepted_data=response_data['Employee_Leave_history']

            for i in range(len(accepted_data)):
                # input_date = datetime.strptime(accepted_data[i]['Start_date'], "%a, %d %b %Y %H:%M:%S %Z")
                start_date = input_date.strftime("%Y-%m-%d")
                input_date = date_convertion( accepted_data[i]['Start_date'] )
                # input_date = datetime.strptime(accepted_data[i]['End_date'], "%a, %d %b %Y %H:%M:%S %Z")
                # end_date = input_date.strftime("%Y-%m-%d")
                end_date = date_convertion( accepted_data[i]['End_date'] )
                accepted_data[i]['Start_date']=start_date
                accepted_data[i]['End_date']=end_date
            return render(request,'user/reject.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,'accepted_data':accepted_data})

        except:
            print("data is not present")
    else:
        print("data is not going",response.status_code)
    return render(request,'user/reject.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})
def leave(request,username,user_type,email,user_id):
    return render(request,'leave.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})
    return HttpResponse("success")
def date_convertion(i_date):
    # accepted_data[i]['Start_date']
    input_date = datetime.strptime(i_date , "%a, %d %b %Y %H:%M:%S %Z")
    start_date = input_date.strftime("%Y-%m-%d")
    return start_date
    
def check(request,username,user_type,email,user_id):
    print(username,user_type,email,user_id)
    data={
        "employee_id":user_id
    }
    print("leave function only callling",data)
    flask_url="http://192.168.0.5:5000/last_record"
    response=requests.post(flask_url,json=data)
    response_data = response.json()
    if response.status_code == 200 :
        # last_approved = ( response_date[0]['Employee_last_history_details']['Approved_By_Whom'] )
        # start_date_approved = date_convertion( response_date[0]['Employee_last_history_details']['Start_date'] )
        # end_date_approved = date_convertion( response_date[0]['Employee_last_history_details']['End_date'] )
        
        # applied_on = date_convertion( response_date[0]['Employee_last_record']['Applied_on'] )
        # start_date_approved = date_convertion( response_date[0]['Employee_last_record']['Start_date'] )
        # end_date_approved = date_convertion( response_date[0]['Employee_last_record']['End_date'] )
        try:
            last_approved = response_data['Employee_last_history_details'][0]['Approved_By_Whom']
            start_date_approved_history = date_convertion(response_data['Employee_last_history_details'][0]['Start_date'])
            end_date_approved_history = date_convertion(response_data['Employee_last_history_details'][0]['End_date'])
        
            applied_on = date_convertion(response_data['Employee_last_record'][0]['Applied_on'])
            start_date_approved_record = date_convertion(response_data['Employee_last_record'][0]['Start_date'])
            end_date_approved_record = date_convertion(response_data['Employee_last_record'][0]['End_date'])
            
            # list = []
            # list.append( last_approved)
            # list.append( start_date_approved_history )
            # list.append( end_date_approved_history )
            # list.append( applied_on)
            # list.append(  start_date_approved_record )
            # list.append( end_date_approved_record )
            return render(request,'user/demo.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,'last_approved':last_approved,'start_date_approved_history':start_date_approved_history,'end_date_approved_history':end_date_approved_history,'applied_on':applied_on,'start_date_approved_record':start_date_approved_record,'end_date_approved_record':end_date_approved_record })
            
            print("this is print", last_approved , start_date_approved_history , end_date_approved_history , applied_on , start_date_approved_record , end_date_approved_record )
            
            print(response.json())
        except:
            return render(request,'user/demo.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type })

    else:
        print("data is not going",response.status_code)
    print("all details",username,user_id,email,user_type)
    
  
    
    #return render(request,'leave.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})
    return render(request,'user/demo.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,'list':list})
    return HttpResponse("success")

def leaveManagement(request,username,user_type,email,user_id):
    data={
        "request":"all_Employee_Names",
        "employee_id":"123",
        "username":"sudha"
    }
    flask_url="http://192.168.0.5:5000/send_all_employee"
    response=requests.post(flask_url,json=data)
    if response.status_code==200:
        response_data=response.json()
        print("this is the response",response_data)
        #names=response_data['Employee_names']
        leaves_data=response_data['employee_leaves_data']
        #print("these are names",names)
        
    else:
        print("some error coming",response.status_code)
    if request.method == 'POST':
        from_Date=request.POST.get('from_date')
        to_Date=request.POST.get('to_date')
        Leave_Type=request.POST.get('leave_type')
        Reason=request.POST.get('reason')
        Selected_Persons=request.POST.getlist('addperson')
        print("leaves",Leave_Type,Reason,Selected_Persons)
        print(from_Date,to_Date)
        dateobject1=datetime.strptime(from_Date,"%Y-%m-%d").date()
        dateobject2=datetime.strptime(to_Date,"%Y-%m-%d").date()
        print("this is date",dateobject1,dateobject2)
        if dateobject1>dateobject2:
            print('this is not good ')
        elif dateobject2>dateobject1:
            data={
                'from_date':from_Date,
                "to_date":to_Date,
                "leave_type":Leave_Type,
                "reason":Reason,
                
                "employee_name":username,
                "id":user_id,
                "request_type":"insert"
            }
            flask_url="http://192.168.0.5:5000/leave_request_data"
            response=requests.post(flask_url,json=data)
            if response.status_code==200:
                response_data=response.json()
                print("this is response data",response_data)
                input_date = datetime.strptime(response_data['From_date'], "%a, %d %b %Y %H:%M:%S %Z")
                from_date1 = input_date.strftime("%Y-%m-%d")
                input_date = datetime.strptime(response_data['To_date'], "%a, %d %b %Y %H:%M:%S %Z")
                to_date1 = input_date.strftime("%Y-%m-%d")
                
                return render(request,'user/demo.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type ,"fromdate":from_date1 , "to_date" : to_date1,"applied_on":response_data['Applied_on']})
            else:
                print("it is not going")
            
    return render(request,'user/demo.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})
    #return render(request,'leave.html',{'data':names,"leaves_data":leaves_data})


def search(request,username,user_type,email,user_id):
    flask_url="http://192.168.0.5:5000/get_employees_count"
    data={
        "request_type":"get_employess"
    }
    response=requests.post(flask_url,json=data)
    response_data=response.json()
    if response.status_code==200:
        try:
           
           Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
           All_Names_Ids=response_data['all_employee_name_id']
           Clock_Info=response_data['Clock_Info']
           print(All_Names_Ids)

           
           print("data is going")
           return render(request,'Admin/search.html',{"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Clock_Info":Clock_Info,
                                                "username":username,'email':email,'user_id':user_id,'user_type':user_type,})
        except:
            print("error is coming at admin page")
    else:
        print("data is not going",response.status_code)
    return render(request,'Admin/search.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,})

def opening(request,username,user_type,email,user_id):
    flask_url="http://192.168.0.5:5000/get_employees_count"
    data={
        "request_type":"get_employess"
    }
    response=requests.post(flask_url,json=data)
    response_data=response.json()
    if response.status_code==200:
        try:
           
           Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
           All_Names_Ids=response_data['all_employee_name_id']
           print(All_Names_Ids)

           
           print("data is going")
           return render(request,'Admin/opening.html',{"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,
                                                "username":username,'email':email,'user_id':user_id,'user_type':user_type,})
        except:
            print("error is coming at admin page")
    else:
        print("data is not going",response.status_code)
    return render(request,'Admin/opening.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,})



def get_Employee_Attendance(request,username,user_type,email,user_id):
    if request.method=="POST":
        name_input=request.POST.get("nameInput")
        user_id=name_input.split(" ")[0]
        user_name=name_input.split(" ")[1]
        print("nameInput",user_id)
        
        flask_url="http://192.168.0.5:5000/get_employee_attendance"
        data={
            "employee_id":user_id
        }
        response=requests.post(flask_url,json=data)
        response_data=response.json()
        if response.status_code==200:
            
            print("respons is ",response_data)
            print(response_data['employee_clock_info'])

            try:
                Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
                All_Names_Ids=response_data['all_employee_name_id']
                Employee_Name=response_data['employee_clock_info'][0]['employee_name']
                print("employee name is",Employee_Name)
                Employee_ID=response_data['employee_clock_info'][0]['Employee_id']
                
                print("employee clock inof",response_data['employee_clock_info'][0])
                Employee_Attendance_Info=response_data['employee_clock_info']
                print(Employee_Attendance_Info)
                 
                
                return render(request,'Admin/search.html',{"Employee_Attendance_Info":Employee_Attendance_Info,"Employee_ID":Employee_ID,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})
            except Exception as e:
                
                Employee_Name=user_name
                Employee_ID=user_id
                Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
                All_Names_Ids=response_data['all_employee_name_id']
                print("error occuring in get_Employee_Attendance mat be data not found")
                return render(request,'Admin/search.html',{"Employee_ID":Employee_ID,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})
        else:
            print("data is not going",response.status_code)
    return render(request,"Admin/search.html",{"username":username,'email':email,'user_id':user_id,'user_type':user_type})


def get_Employee_Leaves(request,username,user_type,email,user_id):
    if request.method=="POST":
        name_input=request.POST.get("nameInput")
        user_id=name_input.split(" ")[0]
        user_name=name_input.split(" ")[1]
        print("nameInput",user_id)
        
        flask_url="http://192.168.0.5:5000/get_leaverequest_data"
        data={
            "employee_id":user_id
        }
        response=requests.post(flask_url,json=data)
        response_data=response.json()
        if response.status_code==200:
            
            print("respons is ",response_data)
            print(".................................")
            print("upto this executed")

            try:
                print("Printing try")
                Employee_Count=int(response_data['Total_employees'][0]['COUNT(Employee_id)'])
                print("employee_count",Employee_Count)
                All_Names_Ids=(response_data['all_employee_name_id'])
                print("allnames",All_Names_Ids)
                Employee_Name=response_data['Employee_Leave_request_data'][0]['Employee_Name']
                print("upto this executed..")
                Employee_ID=response_data['Employee_Leave_request_data'][0]['Employee_id']
                print(All_Names_Ids)
                Employee_LeaveRequest_Info=response_data['Employee_Leave_request_data']
                print("employee leaves data is",Employee_LeaveRequest_Info)
                for i in range(len(Employee_LeaveRequest_Info)):
                    input_date = datetime.strptime(Employee_LeaveRequest_Info[i]['Applied_on'] , "%a, %d %b %Y %H:%M:%S %Z")
                    Applied_on = input_date.strftime("%Y-%m-%d")
                    print("appliedon",Applied_on)
                    print(".......................1")
                    Employee_LeaveRequest_Info[i]['Applied_on']=Applied_on
                    input_date = datetime.strptime(Employee_LeaveRequest_Info[i]['Start_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                    Start_date = input_date.strftime("%Y-%m-%d")
                    Employee_LeaveRequest_Info[i]['Start_date']=Start_date
                    print('start_date:',Start_date)
                    print("......................2")
                    input_date = datetime.strptime(Employee_LeaveRequest_Info[i]['End_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                    End_date = input_date.strftime("%Y-%m-%d")
                    Employee_LeaveRequest_Info[i]['End_date']=End_date
                    print("this is",Employee_LeaveRequest_Info)
                    print("3..................")
                    print("end_date",End_date)
                return render(request,'Admin/leavestats.html',{"Employee_LeaveRequest_Info":Employee_LeaveRequest_Info,"Employee_ID":Employee_ID,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})
            except Exception as e:
                Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
                All_Names_Ids=response_data['all_employee_name_id']
                Employee_Name=user_name
                Employee_ID=user_id
                print("error occuring in get_Employee_leaverequeest mat be data not found",e)
                return render(request,'Admin/leavestats.html',{"Employee_ID":Employee_ID,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})
        else:
            print("data is not going",response.status_code)
    return render(request,"Admin/leavestats.html",{"username":username,'email':email,'user_id':user_id,'user_type':user_type})


def leave_status(request,username,user_type,email,user_id):
    flask_url="http://192.168.0.5:5000/get_employees_count"
    data={
        "request_type":"get_employess"
    }
    response=requests.post(flask_url,json=data)
    response_data=response.json()
    if response.status_code==200:
        try:
           
           Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
           All_Names_Ids=response_data['all_employee_name_id']
           Leave_Request_Info=response_data['Leave_Request_Info']

           print("...................employee id and names...................",All_Names_Ids)
           print("........count...............",Employee_Count)

           print("leave_request_data is.....................",Leave_Request_Info)

           print("data is going")
           for i in range(len(Leave_Request_Info)):
                    input_date = datetime.strptime(Leave_Request_Info[i]['Applied_on'] , "%a, %d %b %Y %H:%M:%S %Z")
                    Applied_on = input_date.strftime("%Y-%m-%d")
                    print("appliedon",Applied_on)
                    print(".......................1")
                    Leave_Request_Info[i]['Applied_on']=Applied_on
                    input_date = datetime.strptime(Leave_Request_Info[i]['Start_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                    Start_date = input_date.strftime("%Y-%m-%d")
                    Leave_Request_Info[i]['Start_date']=Start_date
                    print('start_date:',Start_date)
                    print("......................2")
                    input_date = datetime.strptime(Leave_Request_Info[i]['End_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                    End_date = input_date.strftime("%Y-%m-%d")
                    Leave_Request_Info[i]['End_date']=End_date
                    print("this is",Leave_Request_Info)
                    print("3..................")
                    print("end_date",End_date)










           return render(request,'Admin/leavestats.html',{"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Leave_Request_Info":Leave_Request_Info,
                                                "username":username,'email':email,'user_id':user_id,'user_type':user_type,})
            
        except Exception as e:
            print("error is coming at admin page",e)
    else:
        print("data is not going",response.status_code)
    return render(request,'Admin/leavestats.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})

def org(request,username,user_type,email,user_id):
    data={
        "request":"all_employees"
    }
    flask_url="http://192.168.0.5:5000/get_employees_count"
    response=requests.post(flask_url,json=data)
    if response.status_code==200:
        response_data=response.json()
        print("response data is",response_data)
        try:
            All_Employee_Details=response_data['all_employee_name_id']
            return render(request,'Admin/org.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,
                                          "All_Employee_Details":All_Employee_Details})
        except:
            print("error is coming at org method may be no data found in main table")
    else:
        print("some error coming in org method",response.status_code)
    return render(request,'Admin/org.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})


def update(request,Employee_id,username,user_type,email,user_id):
    data={
        "Employee_id":Employee_id
    }
    flask_url="http://192.168.0.5:5000/employee_details"
    response=requests.post(flask_url,json=data)
    if response.status_code==200:
        response_data=response.json()
        print("response data is",response_data)
        try:
            Complete_Employee_Details=response_data['employee_complete_info']
            input_date = datetime.strptime(Complete_Employee_Details['Date'] , "%a, %d %b %Y %H:%M:%S %Z")
            Date = input_date.strftime("%Y-%m-%d")
            Complete_Employee_Details['Date']=Date
            # All_Employee_Details=response_data['all_employee_name_id']
            return render(request,'Admin/update.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,
                                       "Complete_Employee_Details":Complete_Employee_Details})
        except:
            print("error is coming at org method may be no data found in main table")
    else:
        print("some error coming in org method",response.status_code)
    return render(request,'Admin/update.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})

def festival_data(request,username,user_type,email,user_id):
    date = request.POST.get('festival_date')
    name = request.POST.get('festival_name')
        
    data={
        "date":date,
        "festival_name":name
    }
    flask_url="http://192.168.0.5:5000/holiday"
    response=requests.post(flask_url,json=data)
    if response.status_code==200:
        response_data=response.json()
        print("response data is",response_data)
        return render(request,'Admin/leavestats.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})
    else:
        print("data not going")
    
    return render(request,'Admin/leavestats.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})


def leave_accept(request,Request_id,user_name,user_type,email,user_id):
    userid=Request_id
    username=user_name
    print("this is for accept",Request_id,user_name)
    print("After")
    flask_url=f"http://192.168.0.5:5000/accept/{userid}/{username}"
    response = requests.post(flask_url)
    print(response)
    if response.status_code == 200:
         response_data=response.json()
         Employee_LeaveRequest_Info=response_data['remaining_leaves']
         try:
             for i in range(len(Employee_LeaveRequest_Info)):
                    input_date = datetime.strptime(Employee_LeaveRequest_Info[i]['Applied_on'] , "%a, %d %b %Y %H:%M:%S %Z")
                    Applied_on = input_date.strftime("%Y-%m-%d")
                    print("appliedon",Applied_on)
                    Employee_LeaveRequest_Info[i]['Applied_on']=Applied_on
                    input_date = datetime.strptime(Employee_LeaveRequest_Info[i]['Start_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                    Start_date = input_date.strftime("%Y-%m-%d")
                    Employee_LeaveRequest_Info[i]['Start_date']=Start_date
                    input_date = datetime.strptime(Employee_LeaveRequest_Info[i]['End_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                    End_date = input_date.strftime("%Y-%m-%d")
                    Employee_LeaveRequest_Info[i]['End_date']=End_date
                    print("this is",Employee_LeaveRequest_Info)
             return render(request,'Admin/leavestats.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,"name":"sudhakar","Employee_LeaveRequest_Info":Employee_LeaveRequest_Info})
         except Exception as e:
             print("this is except",e)
             return render(request,'Admin/leavestats.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type})
        # print(data_requested)
    else:
        print(response.status_code)
        return HttpResponse("prindingp")

    return HttpResponse("prindingp")

def leave_reject(request,Request_id,user_name,user_type,email,user_id):
    print("calling leave reject")
    userid=Request_id
    username=user_name
    print("this is for reject",Request_id,user_name)
    flask_url=f"http://192.168.0.5:5000/reject/{userid}/{username}"
    response = requests.post(flask_url)
    if response.status_code == 200:
        response_data=response.json()
        Employee_LeaveRequest_Info=response_data['remaining_leaves']
        # data_requested=response.json()
        # print(data_requested)
        try:
             for i in range(len(Employee_LeaveRequest_Info)):
                    input_date = datetime.strptime(Employee_LeaveRequest_Info[i]['Applied_on'] , "%a, %d %b %Y %H:%M:%S %Z")
                    Applied_on = input_date.strftime("%Y-%m-%d")
                    print("appliedon",Applied_on)
                    Employee_LeaveRequest_Info[i]['Applied_on']=Applied_on
                    input_date = datetime.strptime(Employee_LeaveRequest_Info[i]['Start_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                    Start_date = input_date.strftime("%Y-%m-%d")
                    Employee_LeaveRequest_Info[i]['Start_date']=Start_date
                    input_date = datetime.strptime(Employee_LeaveRequest_Info[i]['End_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                    End_date = input_date.strftime("%Y-%m-%d")
                    Employee_LeaveRequest_Info[i]['End_date']=End_date
                    print("this is",Employee_LeaveRequest_Info)
             return render(request,'Admin/leavestats.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,"name":"sudhakar","Employee_LeaveRequest_Info":Employee_LeaveRequest_Info})
        except Exception as e:
             print("this is except",e)
             return render(request,'Admin/leavestats.html',{"username":username,'email':email,'user_id':user_id,             'user_type':user_type})
    return HttpResponse("successs")



def submit_employee_data(request,username,user_type,email,user_id,Request_type):
    data={
        "request":"all_employees"
    }
    flask_url="http://192.168.0.5:5000/get_employees_count"
    response=requests.post(flask_url,json=data)
    if response.status_code==200:
        response_data=response.json()
        print("response data is",response_data)
        try:
            All_Employee_Details=response_data['all_employee_name_id']
           
        except:
            All_Employee_Details=""
    else:
        print("some error coming in org method",response.status_code)
    if request.method == 'POST':
        data = request.POST.dict()
        print(data)
        new={"request_type":Request_type}
        data.update(new)
        url ="http://192.168.0.5:5000/employee_complete_details"
        response = requests.post(url, json=data)
        if response.status_code == 200:
            data=response.json()
            print("success",data)
            return render(request,'Admin/org.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,
                                                "All_Employee_Details":All_Employee_Details})
        else:
           return render(request,'Admin/org.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,
                                               "All_Employee_Details":All_Employee_Details})
        
    return render(request,'Admin/org.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,
                                        "All_Employee_Details":All_Employee_Details})








#getting fest and employee_leave balance info.............
def Fest_Info(request,username,user_type,email,user_id):
    flask_url = 'http://192.168.0.5:5000/fest_info'
    data = {
        'employee_id':'123'
    }  
    #sending request to flask_url........
    # try:
    response = requests.post(flask_url,json=data)
    #     print('festival ersult',response)   
    # except Exception as e:
    #     print('exception ',e)
    if response.status_code == 200:
        #getting data from falsk...........
        data = response.json()
        print("the flask_data is....",data)
        try:
            Festival_Info=data['Fest_Info']
            Leave_Balance_Info=data['Leave_Balance_Info']
            Announcement_info=data['announcement_info']
            date_of_births=data['date_of_births']
            holiday_info=data['holiday_info']
            leaves_info=data['leaves_info']
            for i in range(len(Festival_Info)):
                input_date = datetime.strptime(Festival_Info[i]['Holiday_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                Start_date = input_date.strftime("%Y-%m-%d")

                Festival_Info[i]['Holiday_date']=Start_date
            print("festival data is",Festival_Info)
        #  print("holiday date is..",Holiday_Date)
        #  print("holiday date is..",current_Date_Formatted)


         #sending fest and leave balance data to html page for displaying..... 
            return render(request,'user/fest_info.html',{'flask_data':Festival_Info,'balance_info':Leave_Balance_Info,"announcement_info":Announcement_info,"date_of_births":date_of_births,"holiday_info":holiday_info,"leaves_info":leaves_info,"username":username,'email':email,'user_id':user_id,'user_type':user_type})
        except Exception as e:
            print("error occuring in Fest INfo function. may be festival data not found")
            Festival_Info=""
        return render(request,'user/fest_info.html',{'flask_data':Festival_Info,'balance_info':Leave_Balance_Info,"username":username,'email':email,'user_id':user_id,'user_type':user_type})
        # return JsonResponse(data)
    else:
        print("error is",response.status_code)
        return JsonResponse({'status': 'error', 'message': 'Failed to send request to Flask app'})








#getting status update data based on request type(last month ,lasth_week ,last_day).............
def Status_Info(request):
    flask_url = 'http://192.168.0.5:5000/admin_get_status'
    data = {
        'Request_Type':'Last_day'
    }  
    #sending request to flask_url........
    response = requests.post(flask_url,json=data)
    if response.status_code == 200:
        #getting data from falsk...........
        data = response.json()
        print("the flask_data is....",data)
        try:
         Status_info=data['Status_Info']
         #sending status update data to html page for displaying..... 
         return render(request,'dailystatus.html',{'flask_data':Status_info})
        except Exception as e:
            print("error occuring in Fest INfo function. may be festival data not found")        
            return render(request,'dailystatus.html',{'flask_data':data})

        # return JsonResponse(data)       
    else:
        print("error is",response.status_code)
        return JsonResponse({'status': 'error', 'message': 'Failed to send request to Flask app'})





#getting fest and employee_leave balance info.............
def Admin_Fest_Info(request,username,user_type,email,user_id):
    flask_url = 'http://192.168.0.5:5000/fest_info'
    data = {
        'employee_id':'123'
    }  
    #sending request to flask_url........
    # try:
    response = requests.post(flask_url,json=data)
    # except Exception as e:
    #     print('exception ',e)
    if response.status_code == 200:
        #getting data from falsk...........
        data = response.json()
        print("the flask_data is....",data)
        try:
         Festival_Info=data['Fest_Info']
        #  Leave_Balance_Info=data['Leave_Balance_Info']
        #  Holiday_Date=Festival_Info[0]['Holiday_date']
        #  current_Date_Formatted= datetime.strptime(Holiday_Date, '%Y-%m-%d')
        #  print("currentlu",current_Date_Formatted)
         for i in range(len(Festival_Info)):
            input_date = datetime.strptime(Festival_Info[i]['Holiday_date'] , "%a, %d %b %Y %H:%M:%S %Z")
            Start_date = input_date.strftime("%Y-%m-%d")
            Festival_Info[i]['Holiday_date']=Start_date
         print("festival data is",Festival_Info)
        #  print("holiday date is..",Holiday_Date)
        #  print("holiday date is..",current_Date_Formatted)
         #sending fest and leave balance data to html page for displaying..... 
         return render(request,'user/fest_info.html',{'flask_data':Festival_Info,"username":username,'email':email,'user_id':user_id,'user_type':user_type})
        except Exception as e:
            print("error occuring in Fest INfo function. may be festival data not found")
            Festival_Info=""
        return render(request,'user/fest_info.html',{'flask_data':Festival_Info,"username":username,'email':email,'user_id':user_id,'user_type':user_type})
        # return JsonResponse(data)
    else:
        print("error is",response.status_code)
        return JsonResponse({'status': 'error', 'message': 'Failed to send request to Flask app'})






#................................................Attendance Info............................................................
    
#getting Attendance data based on request type(last month ,lasth_week ,last_day).............
def Attendance_Info(request,username,user_type,email,user_id,Request_type,Emp_id):
    print(Request_type,Emp_id)
    Flask_Url = 'http://192.168.0.5:5000/admin_get_attendance'
    Data = {
        'Request_Type':Request_type,
        "Emp_id":Emp_id
    }  
    #sending request to flask_url........
    Response = requests.post(Flask_Url,json=Data)
    
    if Response.status_code == 200:
        #getting data from falsk...........
        Data = Response.json()
        print("the flask_data is....",Data)
        try:
             Attendance_Info=Data['Clock_Info']
             Employee_Name=Data['Clock_Info'][0]['employee_name']
        except:
            print("getting error in Attendance info may be data not found")
            Attendance_Info=""
            Employee_Name=""
        Employee_Count=Data['Employee_Count'][0]['COUNT(Employee_id)']
        print("employee",Employee_Count)
        All_Names_Ids=Data['All_Names_Ids']
        try:
         Attendance_Info=Data['Clock_Info']
         Employee_Count=Data['Employee_Count'][0]['COUNT(Employee_id)']
         print("employee",Employee_Count)
         All_Names_Ids=Data['All_Names_Ids']
         Employee_Name=Data['Clock_Info'][0]['employee_name']

         #sending Attendance  data to html page for displaying..... 
         return render(request,'Admin/search.html',{"Employee_Attendance_Info":Attendance_Info,"Employee_ID":Emp_id,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})  
        except Exception as e:
            Attendance_Info=""
            print("error occuring in Fest INfo function. may be festival data not found")        
            return render(request,'Admin/search.html',{"Employee_Attendance_Info":Attendance_Info,"Employee_ID":Emp_id,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})       
         # return JsonResponse(data)       
    else:
        print("error is",Response.status_code)
        return JsonResponse({'status': 'error', 'message': 'Failed to send request to Flask app'})




def status(request,username,user_type,email,user_id,):
    print("calling this funtion")
    if request.method=='POST':
        date=request.POST.get('date')
        completed_tasks=request.POST.get('completed')
        issues=request.POST.get('issues')
        print(completed_tasks,issues)
        feature_targets=request.POST['targets']
        status_update=request.POST['status']
        empid=user_id
        empname=username
        email=email
        # empid=request.POST.get('empid') 
        # empname=request.POST.get('empname')
        print('------------------',completed_tasks)
        print('------------------',issues)
        print('------------------',feature_targets,status_update)
       

        if issues is None:
            issues='No Issues'
   
        data={
            'employeeid':empid,
            'employeename':empname,
            'email':email,
            'completed':completed_tasks,
            'issues':issues,
            'upcoming':feature_targets,
            'statusUpdate':status_update,
            'date':date
        }
        flask_url="http://192.168.0.5:5000/status_update_data"
        response=requests.post(flask_url,json=data)
        flask_response=response.json()
        print(flask_response)
        if response.status_code==200:
            try:
                Status_Data=flask_response['yours_status_data']
                return render(request,'user/status.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,"yours_status_data":Status_Data})
            except:
                print("error coming in status function")
                return render(request,'user/status.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,})
    
    else:
        print('Failed to fetch location details. Status Code:')
    return render(request,'user/status.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,})

def status_update(request,username,user_type,email,user_id):
    print("calling this funtion")
    if request.method=='POST':
        Start_Date=request.POST.get('startdate')
        End_Date=request.POST.get('enddate')
        empid=user_id
        # empid=request.POST.get('empid') 
        # empname=request.POST.get('empname')
        

        
        data={
            'employeeid':empid,
            "start_date":Start_Date,
            "end_date":End_Date,
            "request_type":"in_between_dates"
            }
        flask_url="http://192.168.0.5:5000/get_status_update_data"
        response=requests.post(flask_url,json=data)
        flask_response=response.json()
        print(flask_response)
        if response.status_code==200:
            try:
                Employee_Status_updates=flask_response['request_data']
                for i in range(len(Employee_Status_updates)):
                    Date_input = datetime.strptime(Employee_Status_updates[i]['Date'] , "%a, %d %b %Y %H:%M:%S %Z")
                    Date_change = Date_input.strftime("%Y-%m-%d")
                    Employee_Status_updates[i]['Date']=Date_change
                return render(request,'user/status.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Status_updates":Employee_Status_updates})
            except:
                print("error coming in status_update function")
                return render(request,'user/status.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,})
    
    else:
        print('Failed to fetch location details. Status Code:')
    return render(request,'user/status.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,})






#getting fest and employee_leave balance info.............
def Admin_Holiday_Info(request,username,user_type,email,user_id):
    flask_url = 'http://192.168.0.5:5000/Admin_fest_info'
    data = {
        'employee_id':user_id
    }  
    print("user_id is",user_id)
    #sending request to flask_url........
    # try:
    response = requests.post(flask_url,json=data)
    #     print('festival ersult',response)   
    # except Exception as e:
    #     print('exception ',e)
    if response.status_code == 200:
        #getting data from falsk...........
        data = response.json()
        print("the flask_data is....",data)
        try:
            Festival_Info=data['Fest_Info']
            Announcement_info=data['announcement_info']
            date_of_births=data['date_of_births']
            holiday_info=data['holiday_info']
            leaves_info=data['leaves_info']
            print("Leaves_info",leaves_info)

            for i in range(len(Festival_Info)):
                input_date = datetime.strptime(Festival_Info[i]['Holiday_date'] , "%a, %d %b %Y %H:%M:%S %Z")
                Start_date = input_date.strftime("%Y-%m-%d")
                Festival_Info[i]['Holiday_date']=Start_date
            print("festival data is",Festival_Info)
            print("........................................................")
            for i in range(len(leaves_info)):
               input_date = datetime.strptime(leaves_info[i]['End_date'], "%a, %d %b %Y %H:%M:%S %Z")
               End_date = input_date.strftime("%Y-%m-%d")
               leaves_info[i]['End_date'] = End_date
               input_date2 = datetime.strptime(leaves_info[i]['Start_date'], "%a, %d %b %Y %H:%M:%S %Z")
               Start_date = input_date2.strftime("%Y-%m-%d")
               leaves_info[i]['Start_date'] = Start_date
            print("............................................")
            print("leaves Info.......",leaves_info)
            for i in range(len(holiday_info)):
               input_date = datetime.strptime(holiday_info[i]['Holiday_date'], "%a, %d %b %Y %H:%M:%S %Z")
               Holiday_date = input_date.strftime("%Y-%m-%d")
               holiday_info[i]['Holiday_date'] = Holiday_date
            print("............................................")
            print("leaves Info.......",holiday_info)


            return render(request,'Admin/Admin_fest_info.html',{'flask_data':Festival_Info,"announcement_info":Announcement_info,"date_of_births":date_of_births,"holiday_info":holiday_info,"leaves_info":leaves_info,"username":username,'email':email,'user_id':user_id,'user_type':user_type})
        except Exception as e:
            print("error occuring in Fest INfo function. may be festival data not found")
            Festival_Info=""
        return render(request,'Admin/Admin_fest_info.html',{'flask_data':Festival_Info,"username":username,'email':email,'user_id':user_id,'user_type':user_type})
        # return JsonResponse(data)
    else:
        print("error is",response.status_code)
        return JsonResponse({'status': 'error', 'message': 'Failed to send request to Flask app'})






def Partial_Leave(request, username, user_type, email, user_id):
    print("calling this partial leave function")
    try:
        if request.method == 'POST':
            # from_Date=request.POST.get('startdate')
            # to_Date=request.POST.get('enddate') 
            Select_Time_of_Day=request.POST.get('Select_Time_of_Day')
            # Current_Date=request.POST.get('Current_Date')

            Reason = request.POST.get('reason')
            try:
                from_Date = datetime.now().strftime('%Y-%m-%d')
                to_Date = datetime.now().strftime('%Y-%m-%d')
                print("this is date",from_Date)
                data = {
                    'from_date': from_Date,
                    'to_date':to_Date,
                    "leave_type":Select_Time_of_Day,
                    "reason": Reason,
                    "employee_name": username,
                    "id": user_id,
                    "request_type": "Partial"
                }
                flask_url = "http://192.168.0.5:5000/leave_request_data"
                response = requests.post(flask_url, json=data)
                if response.status_code == 200:
                    response_data = response.json()
                    print("this is response data", response_data)
                    try:
                        return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})
                    except Exception as e:
                        print("error coming in partial function n error is", e)
                        return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})
            except Exception as e:
                print('exception occurred in partial function:', e)
                return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})
        else:
            print('Failed to fetch location details')
            return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})
    except Exception as e:
        print('exception occurred in partial function:', e)
        return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})




def work_from_home(request, username, user_type, email, user_id):
    print("calling this work from home leave function")
    try:
        if request.method == 'POST':
            print("Received form data:", request.POST)
            from_Date = request.POST.get('from_date')
            to_Date = request.POST.get('to_date')
            Reason = request.POST.get('reason')
            print("Received dates:", from_Date, to_Date)
            
            # Check if dates are None before converting
            # if from_Date is None or to_Date is None:
            #     print("......................................................")
            #     return render(request, 'work_from_home.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})
            
            try:
                print(".................................")
                End_date = datetime.strptime(to_Date, '%Y-%m-%d')
                Start_date = datetime.strptime(from_Date, '%Y-%m-%d')
                print("startdate and enddate is",Start_date)
                data = {
                    'from_date': Start_date.strftime('%Y-%m-%d'),
                    'to_date': End_date.strftime('%Y-%m-%d'),
                    'reason': Reason,
                    'employee_name':username,
                    'id': user_id,
                    'request_type':'insert'
                }
                
                flask_url = "http://192.168.0.5:5000/work_from_home"
                response = requests.post(flask_url, json=data)
                
                if response.status_code == 200:
                    response_data = response.json()
                    print("this is response data", response_data)
                    return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})
                else:
                    print("Failed to fetch location details")
                    return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})
            
            except Exception as e:
                print('Exception occurred in work_from_home function:', e)
                return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})
        
        else:
            print('Failed to fetch location details')
            return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})

    except Exception as e:
        print('Exception occurred in work_from_home function:', e)
        return render(request, 'user/clock.html', {"username": username, 'email': email, 'user_id': user_id, 'user_type': user_type})
    



def Work_from_home_accept(request, username, user_type, email, user_id):
    flask_url="http://192.168.0.5:5000/get_employees_count"
    data={
        "request_type":"get_employess"
    }
    response=requests.post(flask_url,json=data)
    response_data=response.json()
    if response.status_code==200:
        try:
           
           Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
           All_Names_Ids=response_data['all_employee_name_id']
           Work_From_Home_Info=response_data['Work_From_Home_Info']
           print(All_Names_Ids)
           print("work from home information.....",Work_From_Home_Info)
           for i in range(len(Work_From_Home_Info)):
               input_date = datetime.strptime(Work_From_Home_Info[i]['Applied_on'], "%a, %d %b %Y %H:%M:%S %Z")
               Applied_on = input_date.strftime("%Y-%m-%d")
               Work_From_Home_Info[i]['Applied_on'] = Applied_on
               input_date2 = datetime.strptime(Work_From_Home_Info[i]['Start_Date'], "%a, %d %b %Y %H:%M:%S %Z")
               Start_Date = input_date2.strftime("%Y-%m-%d")
               Work_From_Home_Info[i]['Start_Date'] = Start_Date
               input_date3 = datetime.strptime(Work_From_Home_Info[i]['End_Date'], "%a, %d %b %Y %H:%M:%S %Z")
               End_Date = input_date3.strftime("%Y-%m-%d")
               Work_From_Home_Info[i]['End_Date'] = End_Date


           
           print("data is going")
           return render(request,'Admin/acceptWFH.html',{"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Work_From_Home_Info":Work_From_Home_Info,
                                                "username":username,'email':email,'user_id':user_id,'user_type':user_type,})
        except:
            print("error is coming at admin page")
    else:
        print("data is not going",response.status_code)
    return render(request,'Admin/acceptWFH.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,})
   



def update_action_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request_id = data.get('requestId')
        action = data.get('action')
        Employee_Id=data.get('EmployeeId')
        # Perform actions based on request_id and action
        print("the status_action n req_id n employee_id.....",action,request_id,Employee_Id)
        Data = {
             'Action_Status':action,
             'request_id':request_id
                }
        flask_url = "http://192.168.0.5:5000/update_work_from_home"
        response = requests.post(flask_url, json=Data)
        if response.status_code == 200:
               print(f'Request {request_id} {action}ed')
               
        # Return success response
        return JsonResponse({'message': 'Action status updated successfully'})
    else:
        # Return error response for unsupported method
        return JsonResponse({'error': 'Method not allowed'}, status=405)

   


def get_Employee_WFHInfo(request,username,user_type,email,user_id):
    if request.method=="POST":
        name_input=request.POST.get("nameInput")
        user_id=name_input.split(" ")[0]
        user_name=name_input.split(" ")[1]
        print("nameInput",user_id)
        
        flask_search="http://192.168.0.5:5000/get_employee_WFH_Info"
        data={
            "employee_id":user_id
        }
        response=requests.post(flask_search,json=data)
        response_data=response.json()
        if response.status_code==200:
            
            print("respons is ",response_data)
            print("upto this...................")
            print(response_data['employee_Emp_WHF_Info'])

            try:
                Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
                print(".................................employee count..................",Employee_Count)
                All_Names_Ids=response_data['all_employee_name_id']
                print(".................................All_Names_Ids..................",All_Names_Ids)

                print("...........................................................")
                Employee_Name=response_data['employee_Emp_WHF_Info'][0]['Employee_Name']

                print("employee name is",Employee_Name)
                Employee_ID=response_data['employee_Emp_WHF_Info'][0]['Employee_Id']
                print("employee_id...............",Employee_ID)

                print("employee wfh info",response_data['employee_Emp_WHF_Info'][0])
                Employee_WFH_Info=response_data['employee_Emp_WHF_Info']
                print(Employee_WFH_Info)  
                
                return render(request,'Admin/acceptWFH.html',{"Employee_WFH_Info":Employee_WFH_Info,"Employee_Id":Employee_ID,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})
            except Exception as e:
                
                Employee_Name=user_name
                Employee_ID=user_id
                Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
                All_Names_Ids=response_data['all_employee_name_id']
                print("error occuring in get_Employee_WFHInfo mat be data not found",e)
                return render(request,'Admin/acceptWFH.html',{"Employee_ID":Employee_ID,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})
        else:
            print("data is not going",response.status_code)
    return render(request,"Admin/acceptWFH.html",{"username":username,'email':email,'user_id':user_id,'user_type':user_type})


# def adminStatus(request,username,user_type,email,user_id):

#     return render(request,"Admin/status.html",{"username":username,'email':email,'user_id':user_id,'user_type':user_type})
    




def get_Employee_status(request,username,user_type,email,user_id):
    if request.method=="POST":
        name_input=request.POST.get("nameInput")
        user_id=name_input.split(" ")[0]
        user_name=name_input.split(" ")[1]
        print("nameInput",user_id)
        
        flask_search="http://192.168.0.5:5000/get_employee_status_Info"
        data={
            "employee_id":user_id
        }
        response=requests.post(flask_search,json=data)
        response_data=response.json()
        if response.status_code==200:
            
            print("response is ",response_data)
            print("upto this...................")
            print(response_data['employee_Emp_Status_Info'])

            try:
                Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
                print(".................................employee count..................",Employee_Count)
                All_Names_Ids=response_data['all_employee_name_id']
                print(".................................All_Names_Ids..................",All_Names_Ids)

                print("...........................................................")
                Employee_Name=response_data['employee_Emp_Status_Info'][0]['Employee_Name']

                print("employee name is",Employee_Name)
                Employee_ID=response_data['employee_Emp_Status_Info'][0]['Employee_id']
                print("employee_id...............",Employee_ID)
                print(",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
                print("employee status info",response_data['employee_Emp_Status_Info'][0])
                employee_Emp_Status_Info=response_data['employee_Emp_Status_Info']
                print(employee_Emp_Status_Info)  
                
                return render(request,'Admin/status.html',{"employee_Emp_Status_Info":employee_Emp_Status_Info,"Employee_ID":Employee_ID,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})
            except Exception as e:
                
                Employee_Name=user_name
                Employee_ID=user_id
                Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
                All_Names_Ids=response_data['all_employee_name_id']
                print("error occuring in get_Employee_WFHInfo mat be data not found",e)
                return render(request,'Admin/status.html',{"Employee_ID":Employee_ID,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})
        else:
            print("data is not going",response.status_code)
    return render(request,"Admin/status.html",{"username":username,'email':email,'user_id':user_id,'user_type':user_type})










def AdminStatusInfo(request, username, user_type, email, user_id):
    flask_url="http://192.168.0.5:5000/get_employees_count"
    data={
        "request_type":"get_employess"
    }
    response=requests.post(flask_url,json=data)
    response_data=response.json()
    if response.status_code==200:
        try:
           print("...........................................................")
           Employee_Count=response_data['Total_employees'][0]['COUNT(Employee_id)']
           All_Names_Ids=response_data['all_employee_name_id']
           Daily_Status_Info=response_data['Daily_Status_Info']
           print(All_Names_Ids)

           
           print("data is going")
           return render(request,'Admin/status.html',{"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Daily_Status_Info":Daily_Status_Info,
                                                "username":username,'email':email,'user_id':user_id,'user_type':user_type,})
        except Exception as e:
            print("error is coming at admin page",e)
    else:
        print("data is not going",response.status_code)
    return render(request,'Admin/status.html',{"username":username,'email':email,'user_id':user_id,'user_type':user_type,})
   

















#................................................Status Info............................................................
    
#getting Status data based on request type(last month ,lasth_week ,last_day).............
def adminStatus(request,username,user_type,email,user_id,Request_type,Emp_id):
    print("upto this executed..............................................")
    print(Request_type,Emp_id)
    Flask_Url = 'http://192.168.0.5:5000/admin_get_status'
    Data = {
        'Request_Type':Request_type,
        "Emp_id":Emp_id
    }  
    #sending request to flask_url........
    Response = requests.post(Flask_Url,json=Data)
    
    if Response.status_code == 200:
        #getting data from falsk...........
        Data = Response.json()
        print("the flask_data is....",Data)
        try:
             Attendance_Info=Data['Status_Info']
             Employee_Name=Data['Status_Info'][0]['Employee_Name']
        except:
            print("getting error in Attendance info may be data not found")
            Attendance_Info=""
            Employee_Name=""
        Employee_Count=Data['Employee_Count'][0]['COUNT(Employee_id)']
        print("employee",Employee_Count)
        All_Names_Ids=Data['All_Names_Ids']
        try:
         Attendance_Info=Data['Status_Info']
         Employee_Count=Data['Employee_Count'][0]['COUNT(Employee_id)']
         print("employee",Employee_Count)
         All_Names_Ids=Data['All_Names_Ids']
         Employee_Name=Data['Status_Info'][0]['Employee_Name']
         print("employee_name................",Employee_Name)

         #sending Attendance  data to html page for displaying.............
         return render(request,'Admin/status.html',{"Employee_Attendance_Info":Attendance_Info,"Employee_ID":Emp_id,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})  
        except Exception as e:
            Attendance_Info=""
            print("error occuring in Fest INfo function. may be festival data not found")        
            return render(request,'Admin/status.html',{"Employee_Attendance_Info":Attendance_Info,"Employee_ID":Emp_id,
                                                     "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})       
         # return JsonResponse(data)       
    else:
        print("error is",Response.status_code)
        return JsonResponse({'status': 'error', 'message': 'Failed to send request to Flask app'})








#................................................Status Info............................................................
    
#getting Status data based on request type(last month ,lasth_week ,last_day).............
# def AdminLeaveStatus(request,username,user_type,email,user_id,Request_type,Emp_id):
#     print("upto this executed..............................................")
#     print(Request_type,Emp_id)
#     Flask_Url = 'http://192.168.0.5:5000/admin_get_Leave_status'
#     Data = {
#         'Request_Type':Request_type,
#         "Emp_id":Emp_id
#     }  
#     #sending request to flask_url........
#     Response = requests.post(Flask_Url,json=Data)
    
#     if Response.status_code == 200:
#         #getting data from falsk...........
#         Data = Response.json()
#         print("the flask_data is....",Data)
#         try:
#              Attendance_Info=Data['Leave_Status_Info']
#              Employee_Name=Data['Leave_Status_Info'][0]['Employee_Name']
#         except:
#             print("getting error in Attendance info may be data not found")
#             Attendance_Info=""
#             Employee_Name=""
#         Employee_Count=Data['Employee_Count'][0]['COUNT(Employee_id)']
#         print("employee",Employee_Count)
#         All_Names_Ids=Data['All_Names_Ids']
#         try:
#          Attendance_Info=Data['Leave_Status_Info']
#          Employee_Count=Data['Employee_Count'][0]['COUNT(Employee_id)']
#          print("employee",Employee_Count)
#          All_Names_Ids=Data['All_Names_Ids']
#          Employee_Name=Data['Leave_Status_Info'][0]['Employee_Name']
#          print("employee_name................",Employee_Name)

#          #sending Attendance  data to html page for displaying.............
#          return render(request,'Admin/leavestats.html',{"Employee_Attendance_Info":Attendance_Info,"Employee_ID":Emp_id,
#                                                      "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})  
#         except Exception as e:
#             Attendance_Info=""
#             print("error occuring in Fest INfo function. may be festival data not found")        
#             return render(request,'Admin/leavestats.html',{"Employee_Attendance_Info":Attendance_Info,"Employee_ID":Emp_id,
#                                                      "username":username,'email':email,'user_id':user_id,'user_type':user_type,"Employee_Count":Employee_Count,"All_Names_Ids":All_Names_Ids,"Employee_Name":Employee_Name})       
#          # return JsonResponse(data)       
#     else:
#         print("error is",Response.status_code)
#         return JsonResponse({'status': 'error', 'message': 'Failed to send request to Flask app'})























            
