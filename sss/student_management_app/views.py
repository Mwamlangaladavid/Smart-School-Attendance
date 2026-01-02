from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from student_management_app.EmailBackEnd import EmailBackEnd
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from student_management_app.models import Students, CustomUser
from django.contrib.auth import authenticate, login

@csrf_exempt
@api_view(['POST'])
def api_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = EmailBackEnd.authenticate(request, username=email, password=password)
    
    if user is not None:
        # Create or get token
        token, created = Token.objects.get_or_create(user=user)
        
        # Convert user_type to readable format
        user_type_map = {
            '1': 'HOD',
            '2': 'Staff', 
            '3': 'Student',
            '4': 'Parent'
        }
        
        return Response({
            'success': True,
            'user_type': user_type_map.get(user.user_type, 'Unknown'),
            'token': token.key,
            'user_id': user.id,
            'email': user.email
        })
    else:
        return Response({
            'success': False,
            'error': 'Invalid credentials'
        }, status=401)

def loginPage(request):
    return render(request, 'login.html')

def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user = EmailBackEnd.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            user_type = user.user_type
            #return HttpResponse("Email: "+request.POST.get('email')+ " Password: "+request.POST.get('password'))
            if user_type == '1':
                return redirect('admin_home')
                
            elif user_type == '2':
                # return HttpResponse("Staff Login")
                return redirect('staff_home')
                
            elif user_type == '4':
                # return HttpResponse("Parent Login")
                return redirect('parent_home')
            else:
                messages.error(request, "Invalid Login!")
                return redirect('login')
        else:
            messages.error(request, "Invalid Login Credentials!")
            #return HttpResponseRedirect("/")
            return redirect('login')

def get_user_details(request):
    if request.user != None:
        return HttpResponse("User: "+request.user.email+" User Type: "+request.user.user_type)
    else:
        return HttpResponse("Please Login First")

def check_username_exists(request):
    username = request.GET.get('username', None)
    data = {
        'exists': CustomUser.objects.filter(username=username).exists()
    }
    return JsonResponse(data)

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')
