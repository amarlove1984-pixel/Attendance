from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import models

from .models import (
    Attendance,
    Enrollment,
    Timetable,
    TeacherSubject,
    TeacherProfile,
    Semester,
    Section,
    Subject,
    Student,
    StudentProfile,
)


# ==========================================
# Attendance
# ==========================================

admin.site.register(Attendance)


# ==========================================
# Enrollment
# ==========================================

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        'subject',
        'semester',
        'section',
        'component',
        'student'
    )

    fields = (
        'subject',
        'semester',
        'section',
        'component',
        'student'
    )

    search_fields = (
        'student__name',
        'student__roll'
    )

    list_filter = (
        'semester',
        'subject',
        'section',
        'component'
    )

    def response_add(
            self,
            request,
            obj,
            post_url_continue=None):

        if "_addanother" in request.POST:

            url = reverse(
                'admin:attendance_enrollment_add'
            )

            return HttpResponseRedirect(
                f"{url}"
                f"?subject={obj.subject.id}"
                f"&semester={obj.semester.id}"
                f"&section={obj.section.id}"
                f"&component={obj.component}"
            )

        return super().response_add(
            request,
            obj,
            post_url_continue
        )

    def get_changeform_initial_data(
            self,
            request):

        initial = super().get_changeform_initial_data(
            request
        )

        initial['subject'] = request.GET.get(
            'subject'
        )

        initial['semester'] = request.GET.get(
            'semester'
        )

        initial['section'] = request.GET.get(
            'section'
        )

        initial['component'] = request.GET.get(
            'component'
        )

        return initial


# ==========================================
# Timetable
# ==========================================

admin.site.register(Timetable)


# ==========================================
# Teacher Subject
# ==========================================

admin.site.register(TeacherSubject)


# ==========================================
# Teacher Profile
# ==========================================




# ==========================================
# Semester
# ==========================================

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return request.user.is_superuser


# ==========================================
# Paper (Section)
# ==========================================

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return request.user.is_superuser


# ==========================================
# Subject
# ==========================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return request.user.is_superuser


# ==========================================
# User Admin
# ==========================================

admin.site.unregister(User)


class CustomUserAdmin(UserAdmin):

    def get_readonly_fields(
            self,
            request,
            obj=None):

        if not request.user.is_superuser:
            return ('email',)

        return ()


admin.site.register(
    User,
    CustomUserAdmin
)

# ==========================================
# Student Admin
# ==========================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'roll',
        'name'
    )

    search_fields = (
        'roll',
        'name'
    )

    def save_model(
            self,
            request,
            obj,
            form,
            change):

        super().save_model(
            request,
            obj,
            form,
            change
        )

        # Create login automatically

        if not User.objects.filter(
                username=obj.roll).exists():

            user = User.objects.create_user(
                username=obj.roll,
                password='00001234',
                first_name=obj.name
            )

            StudentProfile.objects.create(
                user=user,
                student=obj,
                teacher=request.user
            )


# ==========================================
# Student Profile
# ==========================================

from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    exclude = ('user',)

    list_display = (
        'student',
        'user',
        'teacher',
        'phone'
    )
    
@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'designation',
        'department'
    )

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(user=request.user)

    def has_change_permission(
            self,
            request,
            obj=None):

        if request.user.is_superuser:
            return True

        if obj is None:
            return True

        return obj.user == request.user
    

 