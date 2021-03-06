# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 17:20:32 2021

@author: mic5r
"""
from django.urls import path
from eruditoapp import views

app_name= 'eruditoapp'
urlpatterns= [path('about/', views.about, name='about'),
              path('', views.home, name="home"),
              path('subject/', views.subjects, name="subjects"),
              path('subject/<slug:subject_name_slug>/', views.show_subject,
                   name= 'show_subject'),
              path('subject/<slug:subject_name_slug>/<str:sort>', views.show_subject,
                   name= 'show_subject'),
              path("subject/<slug:subject_name_slug>/add_thread/", views.add_thread, name="add_thread"),
              path("subject/<slug:subject_name_slug>/thread/<slug:thread_name_slug>",
                   views.show_thread, name="show_thread"),
              path('register/', views.register, name='register'),
              path('login/', views.user_login, name='login'),
              path('restricted/', views.restricted, name='restricted'),
              path('logout/', views.user_logout, name='logout'),
              path('my-account/', views.my_account, name='my_account'),
              path('register/', views.register, name='register'),
              path('my-account/edit', views.edit_profile, name='edit'),
               path("subject/<slug:subject_name_slug>/thread/<slug:thread_name_slug>/add_comment",
                   views.add_comment, name="add_comment"),
               path('like_comment/', views.LikeCommentView.as_view(), name = 'like_comment'),
               path('like_thread/', views.LikeThreadView.as_view(), name='like_thread'),
               path('user/<slug:user_name_slug>/', views.show_user,
                    name= 'user'),
               path('subject/<slug:subject_name_slug>/useful-resources/',views.useful_resources, name ='useful_resources'),
               path('subject/<slug:subject_name_slug>/search/',views.search_thread, name = 'search'),
              path('subject/<slug:subject_name_slug>/report_thread/<slug:thread_name_slug>',views.report_problem, name='report_thread'),
              path('subject/<slug:subject_name_slug>/report_thread/<slug:thread_name_slug>/<int:comment_id>',views.report_problem, name='report_thread'),
              ]

