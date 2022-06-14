from datetime import datetime
import re, datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.parsers import JSONParser

from .models import Application, Company, Status
from .services import linkedin_job_scrape
from .gmailapi import get_new_mails, new_mail_detail

@permission_classes([IsAuthenticated])
def application(request):
    if request.method == 'GET':
        applications = Application.objects.select_related().filter(applicant=request.user)
        return render(request, 'trackerBoard.html', {'applications':applications})

@permission_classes([IsAuthenticated])
def add_application(request):
    user = request.user
    print(request.POST)

    url = request.POST['url']
    job_info = linkedin_job_scrape(url)
    
    try:
        company = Company.objects.get(name=job_info['company'])
    except:
        company = Company(name=job_info['company'])
        company.save()
    
    application = Application(
        company = company,
        position = job_info['position'],
        location = job_info['location'],
        status = Status.objects.get(id=1),
        job_post = url,
        applicant = user
    )
    application.save()

    return redirect('/application/job/')


@permission_classes([IsAuthenticated])
def to_detil(request, id):
    user = request.user
    applications = Application.objects.select_related().filter(applicant=user)
    application = applications.get(id=id)
    print(application.position)
    status = Status.objects.all()
    return render(request, 'edit-application.html', {'application':application, 'status':status})


@permission_classes([IsAuthenticated])
def edit_application(request, id):
    user = request.user
    applications = Application.objects.select_related().filter(applicant=user)
    application = applications.get(id=id)

    data = request.POST

    company = data.get('company', None)
    position = data.get('position', None)
    location = data.get('location', None)
    status = data.get('status', None)
    job_post = data.get('job_post', None)
    note = data.get('note', None)
    company_email = data.get('company_email', None)

    if company != None and company != "":
        try:
            company = Company.objects.get(name=company)
        except:
            company = new_company = Company(name=company)
            new_company.save()
        application.company = company
    if position != None and position != "":
        application.position = position
    if location != None and location != "":
        application.location = location
    if status != None and status != "":
        application.status = Status.objects.get(name=status)
    if job_post != None and job_post != "":
        application.job_post = job_post
    if note != None and note != "":
        application.note = note
    if company_email != None and company_email != "":
        application.company_email = company_email
        company = application.company
        company_email = re.search('(?<=@).*(?=\.)', company_email).group(0)
        company.company_email = company_email
        company.save()
    application.save()

    return redirect('/application/job/')

@permission_classes([IsAuthenticated])
def del_application(request, id):
    user = request.user
    applications = Application.objects.select_related().filter(applicant=user)
    application = applications.get(id=id)
    application.delete()
    return redirect('/application/job/')


@permission_classes([IsAuthenticated])
def new_mail_checking(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message':'Please login first'})
        
    q = 'is:unread'

    applied_companies = Application.objects.select_related().filter(Q(status=2) | Q(status=3)).values_list('company__company_email')
    email_list = list(applied_companies)
    print(email_list)
    for email in email_list:
        if email[0] != '':
            q += f' from:{email[0]}'
    
    message = ''
    
    if q == 'is:unread':
        message += 'There is no new message.'
        # return JsonResponse({'message':'There is no new message'})

    new = get_new_mails(q)
    new_messages = new.get('messages', [])
    total = new['resultSizeEstimate']

    if total > 1 and len(q.split()) > 2:
        print(f'New {total} follow-ups are waiting for you! Update your application status. {datetime.datetime.now()}')
        message += f'New {total} follow-ups are waiting for you! Update your application status.'
        # return JsonResponse({'message':f'New {total} follow-ups are waiting for you! Update your application status.'})
    elif total == 1:
        # print(new_messages)
        new_message_info = new_mail_detail(new_messages[0]['id'])
        email = new_message_info['payload']['headers'][0]['value']
        # print(re.search('(?<=@).*(?=\.)', email).group(0))
        company = Company.objects.get(company_email=re.search('(?<=@).*(?=\.)', email).group(0))
        # print(f'Check new message from {company.name}! {datetime.datetime.now()}')
        message += f'Check new message from {company.name}!'
        # return JsonResponse({'meesage':f'Check new message from {company.name}!'})
    
    if message == '':
        message = 'No update for today. Apply for new oppotunities!'
        q = None
    else:
        q = q.replace(':', '%3A').replace(' ', '+')
        print(q)
    
    return render(request, 'home.html', {'user': request.user, 'message':message, 'q':q})