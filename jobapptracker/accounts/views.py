import json
import os
from django.shortcuts import render, redirect

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from application.models import Application

credential_file = os.path.join(os.path.dirname(__file__), '../settings/client_secret.json')
credentials = json.load((open(credential_file)))

client_id = credentials['web']['client_id']
api_url = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&include_granted_scopes=true&response_type=code&state=state_parameter_passthrough_value&redirect_uri=http://localhost:8000&client_id=' + client_id


def login(request):
    if not request.user.is_authenticated or request.user.is_admin:
        return render(request, 'login.html')
    else:
        return render(request, 'home.html')


@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    applications = Application.objects.filter(applicant=user)
    applied = applications.filter(status__name = "applied").count()
    interviewd = applications.filter(status__name = "interviewed").count()
    offered = applications.filter(status__name = "offer").count()
    return render(request, 'profile.html', {'user': user, 'applied': applied, 'interviwed':interviewd, 'offered':offered})

@permission_classes([IsAuthenticated])
def edit_view(request):
    return render(request, 'profile-edit.html')

@permission_classes([IsAuthenticated])
def profile_edit(request):
    user = request.user
    print(request.POST)
    phone = request.POST.get('phone')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    
    if phone != None:
        user.phone = phone
    if first_name != None:
        user.first_name = first_name
    if last_name != None:
        user.last_name = last_name
    user.save()

    # return HttpResponse('done')
    return redirect('/accounts/user/')