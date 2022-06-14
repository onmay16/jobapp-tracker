from django.urls import path
from . import views, gmailapi

urlpatterns = [
    path('job/', views.application, name='trackerboard'),
    path('addjob/', views.add_application, name='addjob'),
    path('job/<int:id>/', views.to_detil, name='jobdetail'),
    path('editjob/<int:id>', views.edit_application, name='editjob'),
    path('deljob/<int:id>/', views.del_application, name='deljob'),
    path('notification/', gmailapi.get_new_mails),
    path('newmails/', views.new_mail_checking, name='home')
]