from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.utils import timezone
from datetime import datetime
from django.db.models import Count, Sum, F
import pandas as pd
from django.http import HttpResponse, Http404
import os
import smtplib
from email.mime.text import MIMEText

# Create your views here
def logout(request):
    request.session['user'] = 'None'

    return redirect(homepage)

def homepage(request):
    try:
        user_type = request.session['user']

        if user_type == 'Head':
            return redirect(head_panel)
        elif user_type == 'Teacher':
            return redirect(teacher_panel)
        elif user_type == 'Student':
            return redirect(student_panel)
        elif user_type == 'Parent':
            pass
    except:
        request.session['user'] = 'None'

    message = ''
    
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        choice = request.POST['choice']

        print(email, password, choice)

        if choice == 'Head':
            head_object = Head.objects.filter(email = email, password = password)
            
            if head_object:
                request.session['user'] = 'Head'
                return redirect(head_panel)
            else:
                message = 'Invalid Credentials'
        elif choice == 'Teacher':
            teacher_object = Teacher.objects.filter(email = email, password = password)

            if teacher_object:
                teacher_object = Teacher.objects.get(email = email, password = password)
                request.session['user'] = 'Teacher'
                request.session['id'] = teacher_object.id
                return redirect(teacher_panel)
            else:
                message = 'Invalid Credentials'
        elif choice == 'Student':
            student_object = Student.objects.filter(email = email, password = password)
            
            if student_object:
                student_object = Student.objects.get(email = email, password = password)
                request.session['user'] = 'Student'
                request.session['id'] = student_object.id
                return redirect(student_panel)
            else:
                message = "Invalid Credentials"
        elif choice == 'Parent/Guardian':
            parent_object = Parent.objects.filter(email = email, password = password)
            
            if parent_object:
                parent_object = Parent.objects.get(email = email, password = password)
                request.session['user'] = 'Parent'
                request.session['id'] = parent_object.id
                return redirect(parent_panel)
            else:
                message = "Invalid Credentials"

    return render(request, 'index.html', {'message': message})

def parent_panel(request):
    if request.session['user'] == 'Parent':
        id = request.session['id']
        parent_object = Parent.objects.get(id = id)

        no_children = len(Student.objects.filter(parent = parent_object))
        children_objects = Student.objects.filter(parent = parent_object)

        students = []

        for student in children_objects:
            attendance_object = Attendance.objects.filter(student = student)
            total_classes = Attendance.objects.filter(student = student).count()
            present_classes = Attendance.objects.filter(student = student,is_present=True).count()

            # Calculate the attendance percentage
            if total_classes != 0:
                attendance_percentage = (present_classes / total_classes) * 100
            else:
                attendance_percentage = 0

            student = {'student':student,'total_classes':total_classes, 'attendance': attendance_object, 'percentage':attendance_percentage}
            students.append(student)
        
        
        context = {'parent':parent_object, 'children':no_children, 'students':students}

        return render(request, 'parent_panel.html', context)

def student_panel(request):
    if request.session['user'] == 'Student':
        id = request.session['id']

        student_object = Student.objects.get(id = id)
        attendance_object = Attendance.objects.filter(student = student_object)
        materials = StudyMaterial.objects.filter(batch = student_object.batch)

        total_classes = Attendance.objects.filter(student = student_object).count()
        # Total number of classes where the student was present
        present_classes = Attendance.objects.filter(student = student_object,is_present=True).count()

        # Calculate the attendance percentage
        if total_classes != 0:
            attendance_percentage = (present_classes / total_classes) * 100
        else:
            attendance_percentage = 0

        context = {'student':student_object,'total_classes':total_classes, 'attendance': attendance_object, 'percentage':attendance_percentage, 'files':materials}

        return render(request, 'student_panel.html', context)

def head_panel(request):
    if request.session['user'] == 'Head':
        teachers = Teacher.objects.all()
        batches = Batch.objects.all()

        context = {'teachers':teachers, 'batches':batches}

        return render(request, 'head_panel.html', context)
    else:
        return redirect(homepage)

def add_teacher(request):
    context = {}
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        designation = request.POST['designation']
        subjects = request.POST['subjects']

        if Teacher.objects.filter(email = email):
            context['message'] = 'Email Already Exist'
            return render(request, 'head_panel.html', context)
        else:
            teacher = Teacher(name = name, email = email, password = password, designation = designation, subject = subjects)
            teacher.save()
            print("saved")

    return redirect(head_panel)

def delete_teacher(request, id):
    teacher = Teacher.objects.get(id = id)
    teacher.delete()

    return redirect(head_panel)

def add_batch(request):
    if request.method == 'POST':
        name = request.POST['name']
        date = request.POST['date']
        teacher_id = request.POST['teacher']

        teacher = Teacher.objects.get(id = teacher_id)

        batch = Batch(name = name, start_date = date, teacher = teacher)
        batch.save()

        return redirect(head_panel)

def delete_batch(request, id):
    batch = Batch.objects.get(id = id)
    batch.delete()

    return redirect(head_panel)


def teacher_panel(request):
    if request.session['user'] == 'Teacher':
        id = request.session['id']
        teacher = Teacher.objects.get(id = id)
        batches = Batch.objects.filter(teacher = teacher).annotate(student_count=models.Count('student'))

        context = {'batches':batches, 'teacher':teacher}

        return render(request, 'teacher_panel.html', context)
    else:
        return redirect(homepage)

def add_student(request):
    if request.session['user'] == 'Teacher':
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            phone = request.POST['phone']
            email = request.POST['email']
            password = request.POST['password']
            parent = request.POST['parent']
            batch = request.POST['batch']

            if Student.objects.filter(email = email):
                id = request.session['id']
                teacher = Teacher.objects.get(id = id)
                batches = Batch.objects.filter(teacher = teacher)
                parents = Parent.objects.all()

                context = {'message':'Email Already Exist','teacher':teacher, 'batches':batches, 'parents':parents}
                return render(request, 'add_student.html', context)
            else:
                parent = Parent.objects.get(id = parent)
                batch = Batch.objects.get(id = batch)

                student = Student(first_name = first_name, last_name = last_name, phone = phone, email = email,
                password = password, parent = parent, batch = batch)
                student.save()
                return redirect(teacher_panel)

        id = request.session['id']
        teacher = Teacher.objects.get(id = id)
        batches = Batch.objects.filter(teacher = teacher)
        parents = Parent.objects.all()

        context = {'teacher':teacher, 'batches':batches, 'parents':parents}
        return render(request, 'add_student.html', context)
    else:
        return redirect(homepage)

def add_parent(request):
    if request.session['user'] == 'Teacher':
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            phone = request.POST['phone']
            email = request.POST['email']
            password = request.POST['password']

            if Parent.objects.filter(email = email):
                context = {'message':'Email Already Exist'}
                return render(request, 'add_parent.html', context)
            else:
                parent = Parent(first_name = first_name, last_name = last_name, phone = phone, email = email, password = password)
                parent.save()
                return redirect(add_student)

        id = request.session['id']
        teacher = Teacher.objects.get(id = id)

        context = {'teacher':teacher}
        return render(request, 'add_parent.html', context)
    else:
        return redirect(homepage)
    


def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
    
def mark_attendance(request, id):
    batch = get_object_or_404(Batch, pk=id)
    students = batch.student_set.all()
    teacher = Teacher.objects.get(id = request.session['id'])
    default_date = timezone.now().date()
    attendances = Attendance.objects.filter(date = default_date, student__batch = batch)
    files = StudyMaterial.objects.filter(batch = batch)



    if request.method == 'POST':
        if 'date_change' in request.POST:
            default_date = request.POST['date']
            format = "%Y-%m-%d"
            default_date = datetime.strptime(default_date, format)
            attendances = Attendance.objects.filter(date = default_date, student__batch = batch)
        else:
            date = request.POST.get('date', timezone.now().date())
            for student in students:
                is_present = request.POST.get(f'student_{student.id}', False)
                if is_present == 'on':
                    is_present = True

                present_attendance = Attendance.objects.filter(student = student, date = date, student__batch = batch)

                if present_attendance:
                    present_attendance.update(student=student, date=date, is_present=is_present, marked_by=teacher)
                    
                else:
                    Attendance.objects.create(student=student, date=date, is_present=is_present, marked_by=teacher)
                    if is_present == True:
                        pass
                    else:
                        # MAIL 
                        subject = f"School Notification - {student.first_name}"
                        body = f"{student.first_name} {student.last_name} is not Present today - {date}"
                        sender = "attendancemanagementsystem7@gmail.com"
                        recipients = [student.parent.email]
                        password = "qesy fhfc ybrf ludp"
                        send_email(subject, body, sender, recipients, password)
                
                format = "%Y-%m-%d"
                default_date = datetime.strptime(date, format)
                attendances = Attendance.objects.filter(date = default_date, student__batch = batch)

    return render(request, 'mark_attendance.html', {'files':files, 'batch': batch, 'students': students, 'teacher':teacher, 'default_date': default_date, "attendances":attendances})

def notice(request,id):
    batch = Batch.objects.get(id = id)
    teacher = ''
    if request.session['user'] == 'Teacher':
        teacher = Teacher.objects.get(id = request.session['id'])
    

    if request.method == 'POST':
        text = request.POST['text']

        notice_obj = Notice(text = text, batch = batch)
        notice_obj.save()
    notices = Notice.objects.filter(batch = batch)[::-1]

    return render(request, 'notice.html', {'batch': batch, 'teacher':teacher, 'notices':notices})

def parent_notice(request):
    batch_notices = []

    parent_object = Parent.objects.get(id = request.session['id'])
    student_objects = Student.objects.filter(parent = parent_object)

    for student in student_objects:
        notice_object = Notice.objects.filter(batch = student.batch)[::-1]
        batch_notices.append([student,notice_object])
    print(batch_notices)
        
    # notices = Notice.objects.filter(batch = batch)[::-1]

    return render(request, 'parent_notice.html', {'batch_notices':batch_notices})

def batch_attendance_summary(request, batch_id):
    # Get the batch object
    batch = Batch.objects.get(id=batch_id)
    teacher = Teacher.objects.get(id = request.session['id'])

    # Get all students belonging to the batch
    students = Student.objects.filter(batch=batch)

    attendance_summary = {}

    for student in students:
        attendance = Attendance.objects.filter(student = student)
        
        total = 0
        present = 0

        for day in attendance:
            total += 1
            if day.is_present:
                present += 1

        percent = (present/total)*100
        
        attendance_summary[student.id] = [student.first_name + ' ' + student.last_name, total, present, (present/total)*100]
    if attendance_summary:
        attendance_summary = pd.DataFrame(attendance_summary).T

        attendance_summary.columns = ['Name','Total Days', 'Present Days', "Percent"]
        attendance_summary.reset_index(drop = True, inplace = True)
        attendance_summary.index += 1 
        attendance_summary = attendance_summary.to_html(classes= "table table-info table-striped-columns mt-5")

        return render(request, 'attendance_summary.html', {'batch': batch, 'attendance_summary': attendance_summary, 'teacher':teacher})
    else:
        return redirect(teacher_panel)
    
def upload_file(request):
    if request.method == 'POST':
        batch_id = request.POST['batch_id']
        batch = Batch.objects.get(id = batch_id)
        file = request.FILES.get('file')
        if file:
            StudyMaterial.objects.create(batch=batch, file=file, file_name = str(file))
            return redirect(mark_attendance, batch_id)  # Redirect to a new URL
        else:
            return HttpResponse('No file selected.', status=400)


def delete_file(request, id):

    file = StudyMaterial.objects.get(id = id)
    batch_id = file.batch.id
    file.delete()

    return redirect(mark_attendance, batch_id)


def download_study_material(request, file_id):
    try:
        study_material = StudyMaterial.objects.get(id=file_id)
        # Optional: Check if request.user is in the study material's batch
        file_path = study_material.file.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/force-download")
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        raise Http404("File does not exist")
    except StudyMaterial.DoesNotExist:
        raise Http404("Study material not found")