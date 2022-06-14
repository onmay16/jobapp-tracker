import requests
from decouple import config

from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.forms import ValidationError

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from dj_rest_auth.registration.views import SocialLoginView

from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from json.decoder import JSONDecodeError

from settings import credentials
from .models import User

BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/callback/'
client_id = config('client_id')
client_secret = config('client_secret')
state = config('STATE')

def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email " + "https://www.googleapis.com/auth/userinfo.profile"
    google_auth_api = "https://accounts.google.com/o/oauth2/v2/auth"

    return redirect(f"{google_auth_api}?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

def google_callback(request):
    code = request.GET.get('code')
    # get access token
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')
    id_token = token_req_json.get('id_token')

    # get user google email
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?id_token={id_token}")
    email_req_status = email_req.status_code
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    email_req_json = email_req.json()
    email = email_req_json.get('email')

    # get user info
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo", 
        params={
            'access_token': access_token
        })
    if not user_info_response.ok:
        raise ValidationError('Failed to obtain user info from Google.')
    user_info = user_info_response.json()
    
    profile_data = {
        'first_name': user_info.get('given_name', ''),
        'last_name': user_info.get('family_name', '')
    }
    
    try:
        user = User.objects.get(email=email)
        # user already registered
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        print(accept_status)
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        login(request, user)
        return redirect('/application/newmails')
    except:
        # user not registered yet
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        user = User.objects.get(email=email)
        user.first_name = profile_data['first_name']
        user.last_name = profile_data['last_name']
        user.save()
        login(request, user)
        return redirect('/application/job/')

class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client

@permission_classes([IsAuthenticated])
def signout(request):
        logout(request)
        return redirect('/accounts/login/')

