from django.contrib import admin
from .models import *
admin.site.register([Semester,Section,Subject,Student,SubjectAllocation,Attendance])
