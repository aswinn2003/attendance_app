from django.db import models

# Create your models here.

class Head(models.Model):
    name = models.CharField(max_length = 120)
    password = models.CharField(max_length = 120)
    email = models.CharField(max_length = 210)

    def __str__(self):
        return self.name
    
class Teacher(models.Model):
    name = models.CharField(max_length = 120)
    email = models.CharField(max_length = 120)
    password = models.CharField(max_length = 120)
    designation = models.CharField(max_length = 120)
    subject = models.CharField(max_length = 500)
    added_by = models.ForeignKey(Head,on_delete = models.SET_NULL, blank = True, null = True)

    def __str__(self):
        return self.name
    
BATCH_STATUS = (
    ("ONGOING", "ONGOING"),
    ("COMPLETED", "COMPLTED"),
)

class Batch(models.Model):
    name = models.CharField(max_length = 120)
    start_date = models.DateField(blank = True, null = True)
    teacher = models.ForeignKey(Teacher, on_delete = models.SET_NULL, default = None, blank = True, null = True)
    status = models.CharField(max_length = 120, choices = BATCH_STATUS, default = "ONGOING", blank = True, null = True)

    def __str__(self):
        return self.name
    
class Parent(models.Model):
    first_name = models.CharField(max_length = 120)
    last_name = models.CharField(max_length = 120)
    phone = models.CharField(max_length = 120)
    email = models.CharField(max_length = 120)
    password = models.CharField(max_length = 120)

    def __str__(self):
        return self.first_name + self.last_name
    
class Student(models.Model):
    first_name = models.CharField(max_length = 120)
    last_name = models.CharField(max_length = 120)
    phone = models.CharField(max_length = 120)
    email = models.CharField(max_length = 120)
    password = models.CharField(max_length = 120)
    parent = models.ForeignKey(Parent, on_delete = models.SET_NULL, default = None, blank = True, null = True)
    batch = models.ForeignKey(Batch, on_delete = models.SET_NULL, default = None, blank = True, null = True)

    def __str__(self):
        return self.first_name + self.last_name
    
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.date}"


class StudyMaterial(models.Model):
    batch = models.ForeignKey(Batch, related_name='study_materials', on_delete=models.CASCADE)
    file = models.FileField(upload_to='study_materials/')
    file_name = models.CharField(max_length = 200, blank = True, null = True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Material for {self.batch.name} uploaded on {self.uploaded_at.strftime('%Y-%m-%d')}"
    

class Notice(models.Model):
    text = models.CharField(max_length = 2000, blank = True, null = True)
    batch = models.ForeignKey(Batch, on_delete = models.CASCADE)
    time = models.DateField(auto_now_add = True)