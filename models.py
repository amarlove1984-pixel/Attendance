from django.db import models

class Semester(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Student(models.Model):
    roll = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.roll} - {self.name}"
    
from django.contrib.auth.models import User

from django.contrib.auth.models import User

class StudentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.student.name