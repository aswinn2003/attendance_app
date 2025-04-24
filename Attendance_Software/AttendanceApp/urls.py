from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name = "homepage"),
    path('head_panel/', views.head_panel, name = "head_panel"),
    path('teacher_panel/', views.teacher_panel, name = "teacher_panel"),
    path('add_teacher/', views.add_teacher, name = "add_teacher"),
    path('delete_teacher/<int:id>/', views.delete_teacher, name = "delete_teacher"),
    path('add_batch/', views.add_batch, name = "add_batch"),
    path('delete_batch/<int:id>/', views.delete_batch, name = "delete_batch"),
    path('logout/', views.logout, name = "logout"),
    path('add_student/', views.add_student, name = "add_student"),
    path('add_parent/', views.add_parent, name = "add_parent"),
    path('mark_attendance/<int:id>/', views.mark_attendance, name = "mark_attendance"),
    path('batch_attendance_summary/<int:batch_id>/', views.batch_attendance_summary, name = "batch_attendance_summary"),
    path('upload_file/', views.upload_file, name = "upload_file"),
    path('materials/download/<int:file_id>/', views.download_study_material, name='download_study_material'),
    path('delete_file/<str:id>/', views.delete_file, name = "delete_file"),
    path('student_panel/', views.student_panel, name = "student_panel"),
    path('notice/<int:id>/', views.notice, name = "notice"),
    path('parent_panel/', views.parent_panel, name = "parent_panel"),
    path('parent_notice/', views.parent_notice, name = "parent_notice"),
]
