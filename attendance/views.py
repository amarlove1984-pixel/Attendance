from urllib import request

from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import TeacherSubject
from django.http import HttpResponse
import openpyxl
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import *
from django.conf import settings
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle
)
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

from django.core.mail import send_mail


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Attendance



       
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io
import base64
from .models import Attendance, Student

@login_required
def analytics_dashboard(request):

    if request.user.is_superuser:
        allowed = Enrollment.objects.all()
    else:
        allowed = get_teacher_enrollments(request.user)

    total_students = Student.objects.filter(
        enrollment__in=allowed
    ).distinct().count()

    present = Attendance.objects.filter(
        enrollment__in=allowed,
        status='P'
    ).count()

    absent = Attendance.objects.filter(
        enrollment__in=allowed,
        status='A'
    ).count()

    fig, ax = plt.subplots(figsize=(6, 6))

    if present == 0 and absent == 0:

        ax.text(
            0.5,
            0.5,
            "No Attendance Data Available",
            fontsize=18,
            ha='center',
            va='center'
        )

        ax.axis('off')

    else:

        ax.pie(
            [present, absent],
            labels=['Present', 'Absent'],
            autopct='%1.1f%%'
        )

        ax.set_title(
            "Attendance Distribution"
        )

    buffer = io.BytesIO()

    plt.savefig(buffer, format='png')

    buffer.seek(0)

    image_png = buffer.getvalue()

    graph = base64.b64encode(image_png)

    graph = graph.decode('utf-8')

    buffer.close()

    plt.close()

    return render(
        request,
        'analytics_dashboard.html',
        {
            'graph': graph,
            'students': total_students,
            'present': present,
            'absent': absent
        }
    )
    
    
@login_required
def send_defaulter_alerts(request):

    students = StudentProfile.objects.filter(
        student__enrollment__in=
        get_teacher_enrollments(request.user)
    ).distinct()

    sent = 0

    for sp in students:

        enrollments = Enrollment.objects.filter(
            student=sp.student
        )

        total = Attendance.objects.filter(
            enrollment__in=enrollments
        ).count()

        present = Attendance.objects.filter(
            enrollment__in=enrollments,
            status='P'
        ).count()

        percentage = 0

        if total > 0:

            percentage = (
                present/total
            )*100

        if percentage < 75:

            send_mail(

                'Low Attendance Alert',

                f'Your attendance is '
                f'{percentage:.2f}%.\n'
                f'Please improve it.',

                settings.EMAIL_HOST_USER,

                [sp.user.email],

                fail_silently=False

            )

            sent += 1

    messages.success(
        request,
        f'{sent} alerts sent.'
    )

    return redirect('dashboard')



@login_required
def export_pdf(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename=attendance.pdf'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=letter
    )

    elements = []

    data = [[
        'Date',
        'Roll',
        'Name',
        'Subject',
        'Status'
    ]]

    if request.user.is_superuser:
        if request.user.is_superuser:
            records = Attendance.objects.all()
        else:
            records = Attendance.objects.filter(
                enrollment__in=
                get_teacher_enrollments(request.user)
            )
    else:
        records = Attendance.objects.filter(
            enrollment__in=
            get_teacher_enrollments(request.user)
        )

    for r in records:

        data.append([

            str(r.attendance_date),

            r.enrollment.student.roll,

            r.enrollment.student.name,

            r.enrollment.subject.name,

            r.get_status_display()

        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ('BACKGROUND',(0,0),(-1,0),colors.grey),

        ('GRID',(0,0),(-1,-1),1,colors.black)

    ]))

    elements.append(table)

    doc.build(elements)

    return response



@login_required
def change_password(request):

    if request.method == 'POST':

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                'Password changed successfully.'
            )

            return redirect('dashboard')

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        'change_password.html',
        {'form': form}
    )
      
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

@staff_member_required
def factory_reset(request):

    if not request.user.is_superuser:
        messages.error(request, "Only Super Admin can perform Factory Reset.")
        return redirect('dashboard')

    if request.method == 'POST':

        Attendance.objects.all().delete()

        messages.success(
            request,
            'All attendance records deleted successfully.'
        )

        return redirect('dashboard')

    return render(
        request,
        'factory_reset.html'
    )    
       
from django.contrib.auth import authenticate, login
from django.contrib import messages

def teacher_login(request):

    if request.method == 'POST':

        if not request.POST.get('remember_me'):
            request.session.set_expiry(0)

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_staff:
                return redirect('dashboard')
            else:
                return redirect('student_dashboard')

        else:
            messages.error(
                request,
                'Invalid Roll Number/Employee ID or Password'
            )

    return render(request, 'login.html')

def teacher_logout(request):

    logout(request)

    return redirect('login')
from .models import (
    Semester,
    Subject,
    Section,
    Enrollment,
    Attendance,
    TeacherSubject
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect


@login_required
def profile(request):

    if request.user.is_staff:

        profile, created = TeacherProfile.objects.get_or_create(
            user=request.user
        )

        if request.method == 'POST':

            profile.designation = request.POST.get('designation')
            profile.department = request.POST.get('department')
            profile.phone = request.POST.get('phone')
            profile.blood_group = request.POST.get('blood_group')
            profile.address = request.POST.get('address')
            profile.qualification = request.POST.get('qualification')
            profile.emergency_contact = request.POST.get(
                'emergency_contact'
            )

            if request.POST.get('joining_date'):
                profile.joining_date = request.POST.get(
                    'joining_date'
                )

            if request.POST.get('date_of_birth'):
                profile.date_of_birth = request.POST.get(
                    'date_of_birth'
                )

            if request.FILES.get('photo'):
                profile.photo = request.FILES['photo']

            profile.save()

            messages.success(
                request,
                'Profile updated successfully.'
            )

            return redirect('profile')

        return render(
            request,
            'profile.html',
            {
                'teacher_profile': profile
            }
        )

    # STUDENT PROFILE

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        profile.phone = request.POST.get('phone')
        profile.email = request.POST.get('email')
        profile.address = request.POST.get('address')
        profile.blood_group = request.POST.get('blood_group')
        profile.gender = request.POST.get('gender')
        profile.guardian_name = request.POST.get(
            'guardian_name'
        )
        profile.guardian_phone = request.POST.get(
            'guardian_phone'
        )
        profile.emergency_contact = request.POST.get(
            'emergency_contact'
        )

        if request.POST.get('date_of_birth'):
            profile.date_of_birth = request.POST.get(
                'date_of_birth'
            )

        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']

        profile.save()

        messages.success(
            request,
            'Profile updated successfully.'
        )

        return redirect('profile')

    return render(
        request,
        'profile.html',
        {
            'student_profile': profile
        }
    )
       
import pandas as pd

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import StudentUploadForm
from .forms import TeacherProfileForm

from .models import Student, Enrollment, StudentProfile


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
import pandas as pd

from .forms import StudentUploadForm
from .models import Student, StudentProfile, Enrollment


def upload_students(request):

    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':

        form = StudentUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            excel = request.FILES['excel_file']

            subject = form.cleaned_data['subject']
            semester = form.cleaned_data['semester']
            section = form.cleaned_data['section']
            component = form.cleaned_data['component']

            df = pd.read_excel(excel)

            new_students = 0
            new_enrollments = 0

            for _, row in df.iterrows():

                roll = str(row.iloc[0]).strip()
                name = str(row.iloc[1]).strip()
                reg = str(row.iloc[2]).strip()

                # Create or update student
                student, created = Student.objects.get_or_create(
                    roll=roll
                )

                # Always update details
                student.name = name

                # Only if this field exists in Student model
                if hasattr(student, 'registration_number'):
                    student.registration_number = reg

                student.save()

                # Create or get login account
                user, user_created = User.objects.get_or_create(
                    username=roll,
                    defaults={
                        'first_name': name
                    }
                )

                # Update user name every time
                user.first_name = name

                if user_created:
                    user.set_password('00001234')

                user.save()

                # Create profile if not present
                profile, profile_created = StudentProfile.objects.get_or_create(
                    student=student,
                    defaults={
                        'user': user,
                        'teacher': request.user
                    }
                )

                # Update profile if it already exists but has no user
                if not profile.user:
                    profile.user = user

                profile.teacher = request.user
                profile.save()

                # Enroll student if not already enrolled
                enrollment, enrollment_created = Enrollment.objects.get_or_create(
                    student=student,
                    subject=subject,
                    semester=semester,
                    section=section,
                    component=component
                )
            messages.success(
                request,
                'Students imported successfully.'
            )
            messages.success(
                request,
                f"{new_students} new students created and "
                f"{new_enrollments} new enrollments added."
            )
            return redirect('dashboard')

    else:
        form = StudentUploadForm()

    return render(
        request,
        'upload_students.html',
        {'form': form}
    )    
                    
@login_required
def my_pdf(request):

    profile = StudentProfile.objects.get(
        user=request.user
    )

    attendance = Attendance.objects.filter(
        enrollment__student=profile.student
    )

    # Generate PDF here
        
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from datetime import date

@login_required
def take_attendance(request):

    if not request.user.is_staff:
        raise PermissionDenied()

    enrollments = []

    # Teacher-wise restriction
    allowed_enrollments = get_teacher_enrollments(
        request.user
    )

    if request.user.is_superuser:

        teacher_subjects = Subject.objects.all()

        teacher_sections = Section.objects.all()

        teacher_semesters = Semester.objects.all()

    else:

        teacher_profile = TeacherProfile.objects.get(
            user=request.user
        )

        teacher_profile = TeacherProfile.objects.get(
            user=request.user
        )

        teacher_subjects = Subject.objects.filter(
            teachersubject__teacher=teacher_profile
        ).distinct()

        teacher_sections = Section.objects.filter(
            enrollment__in=allowed_enrollments
        ).distinct()

        teacher_semesters = Semester.objects.filter(
            enrollment__in=allowed_enrollments
        ).distinct()
    
    
    if request.method == 'POST':

        semester_id = request.POST.get('semester')
        section_id = request.POST.get('section')
        subject_id = request.POST.get('subject')
        component = request.POST.get('component')

        attendance_date = request.POST.get('date')

        if not attendance_date:
            attendance_date = date.today()

        double_period = request.POST.get(
            'double_period'
        )

        period_count = 2 if double_period else 1

        enrollments = allowed_enrollments.filter(
            semester_id=semester_id,
            subject_id=subject_id,
            section_id=section_id,
            component=component
        ).select_related(
            'student',
            'subject',
            'semester',
            'section'
        )

        # Save attendance
        if 'save_attendance' in request.POST:

            if not enrollments.exists():

                messages.error(
                    request,
                    "No students found."
                )

            else:

                for enrollment in enrollments:

                    status = request.POST.get(
                        f'status_{enrollment.id}',
                        'P'
                    )

                    # Only one attendance per day
                    if not settings.ALLOW_MULTIPLE_ATTENDANCE_SAME_DAY:

                        attendance, created = (
                            Attendance.objects.update_or_create(
                                enrollment=enrollment,
                                teacher=request.user,
                                attendance_date=attendance_date,

                                defaults={
                                    'status': status,
                                    'period_count': period_count
                                }
                            )
                        )

                    # Multiple attendance allowed
                    else:

                        Attendance.objects.create(
                            enrollment=enrollment,
                            teacher=request.user,
                            attendance_date=attendance_date,
                            status=status,
                            period_count=period_count
                        )

                messages.success(
                    request,
                    "Attendance saved successfully."
                )

                return redirect('take_attendance')

    return render(
        request,
        'attendance_form.html',
        {
            'subjects': teacher_subjects,
            'sections': teacher_sections,
            'semesters': teacher_semesters,
            'enrollments': enrollments,
            'today': date.today()
        }
    )
    
from .models import StudentProfile


def calculate_percentage(student):

    attendances = Attendance.objects.filter(
        enrollment__student=student
    )

    total_classes = sum(
        a.period_count for a in attendances
    )

    present_classes = sum(
        a.period_count
        for a in attendances
        if a.status == 'P'
    )

    if total_classes == 0:
        return 0

    return round(
        (present_classes / total_classes) * 100,
        2
    )


   
from .models import Student, Attendance, Enrollment


@login_required
def percentage_report(request):

    if not request.user.is_staff:
        raise PermissionDenied()

    students = []

    students_set = set()

    # Get only students assigned to this teacher
    for enrollment in get_teacher_enrollments(
            request.user):

        students_set.add(
            enrollment.student
        )

    for student in students_set:

        enrollments = Enrollment.objects.filter(
            student=student
        )

        attendance_records = Attendance.objects.filter(
            enrollment__in=enrollments
        )

        # Count actual classes considering double periods
        total = sum(
            attendance.period_count
            for attendance in attendance_records
        )

        present = sum(
            attendance.period_count
            for attendance in attendance_records
            if attendance.status == 'P'
        )

        absent = total - present

        percentage = 0

        if total > 0:

            percentage = round(
                (present / total) * 100,
                2
            )

        # Row colour
        if percentage >= 75:
            color = "success"      # Green

        elif percentage >= 60:
            color = "warning"      # Yellow

        else:
            color = "danger"       # Red

        students.append({

            'student': student,

            'present': present,

            'absent': absent,

            'total': total,

            'percentage': percentage,

            'color': color

        })

    # Sort by percentage (lowest first)
    students = sorted(
        students,
        key=lambda x: x['percentage']
    )

    return render(
        request,
        'percentage.html',
        {
            'students': students
        }
    )   
    
        
from django.core.paginator import Paginator

@login_required
def student_history(request):

    roll = request.GET.get('roll', '')

    if request.user.is_superuser:
        records = Attendance.objects.all()
    else:
        records = Attendance.objects.filter(
            enrollment__in=
            get_teacher_enrollments(request.user)
        )
    if roll:
        records = records.filter(
            enrollment__student__roll__icontains=roll
        )

    records = records.order_by('-attendance_date')

    paginator = Paginator(records, 20)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'history.html',
        {
            'page_obj': page_obj,
            'roll': roll
        }
    )
    
    
@login_required
def defaulter_report(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    students = []

    students_set = set()

    for enrollment in get_teacher_enrollments(
            request.user):

        students_set.add(
            enrollment.student
        )

    for student in students_set:

        enrollments = Enrollment.objects.filter(
            student=student
        )

        total = Attendance.objects.filter(
            enrollment__in=enrollments
        ).count()

        present = Attendance.objects.filter(
            enrollment__in=enrollments,
            status='P'
        ).count()

        percentage = 0

        if total > 0:

            percentage = round(
                (present/total)*100,
                2
            )

        if percentage < 75:

            students.append({

                'student': student,

                'percentage': percentage

            })

    return render(
        request,
        'defaulters.html',
        {'students': students}
    )

@login_required
def edit_attendance(request):

    records = Attendance.objects.all().order_by(
        '-attendance_date'
    )

    if request.method == 'POST':

        attendance_id = request.POST.get(
            'attendance_id'
        )

        status = request.POST.get('status')

        attendance = Attendance.objects.get(
            id=attendance_id
        )

        attendance.status = status
        attendance.save()

        return redirect('edit_attendance')

    return render(
        request,
        'edit_attendance.html',
        {'records': records}
    )
    
@login_required
def attendance_report(request):

    if not request.user.is_staff:
        raise PermissionDenied()

    allowed_enrollments = get_teacher_enrollments(
        request.user
    )

    records = Attendance.objects.filter(
        enrollment__in=allowed_enrollments
    ).select_related(
        'enrollment__student',
        'enrollment__semester',
        'enrollment__subject',
        'enrollment__section'
    )

    # ==========================================
    # Dropdown data
    # ==========================================

    if request.user.is_superuser:

        subjects = Subject.objects.all()

        semesters = Semester.objects.all()

        sections = Section.objects.all()

    else:

        try:

            teacher_profile = TeacherProfile.objects.get(
                user=request.user
            )

            subjects = Subject.objects.filter(
                teachersubject__teacher=teacher_profile
            ).distinct()

        except TeacherProfile.DoesNotExist:

            subjects = Subject.objects.none()

        semesters = Semester.objects.filter(
            enrollment__in=allowed_enrollments
        ).distinct()

        sections = Section.objects.filter(
            enrollment__in=allowed_enrollments
        ).distinct()

    # ==========================================
    # Filters
    # ==========================================

    semester_id = request.GET.get('semester')
    subject_id = request.GET.get('subject')
    section_id = request.GET.get('section')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    month_year = request.GET.get('month_year')

    if semester_id:

        records = records.filter(
            enrollment__semester_id=semester_id
        )
    
        # Date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    month_year = request.GET.get('month_year')

    if start_date:
        records = records.filter(
            attendance_date__gte=start_date
        )

    if end_date:
        records = records.filter(
            attendance_date__lte=end_date
        )

    # Month-Year filter
    if month_year:
        try:
            year, month = month_year.split('-')

            records = records.filter(
                attendance_date__year=int(year),
                attendance_date__month=int(month)
            )

        except ValueError:
            pass
        
    if subject_id:

        records = records.filter(
            enrollment__subject_id=subject_id
        )

    if section_id:

        records = records.filter(
            enrollment__section_id=section_id
        )

    if start_date:
        records = records.filter(
            attendance_date__gte=start_date
        )

    if end_date:
        records = records.filter(
            attendance_date__lte=end_date
        )

    if month_year:
        try:
            year, month = month_year.split('-')

            records = records.filter(
                attendance_date__year=int(year),
                attendance_date__month=int(month)
            )

        except ValueError:
            pass
        
    return render(
        request,
        'attendance_report.html',
        {
            'records': records,

            'subjects': subjects,
            'semesters': semesters,
            'sections': sections,

            'selected_semester': semester_id,
            'selected_subject': subject_id,
            'selected_section': section_id,

            'start_date': start_date,
            'end_date': end_date,
            'month_year': month_year,
        }
    )
    
       
from django.http import HttpResponse
import openpyxl


@login_required
def export_excel(request):

    wb = openpyxl.Workbook()
    ws = wb.active

    ws.title = "Attendance Report"

    headers = [
        "Date",
        "Roll",
        "Name",
        "Subject",
        "Component",
        "Section",
        "Status"
    ]

    ws.append(headers)

    if request.user.is_superuser:
        if request.user.is_superuser:
            records = Attendance.objects.all()
        else:
            records = Attendance.objects.filter(
                enrollment__in=
                get_teacher_enrollments(request.user)
            )
    else:
        records = Attendance.objects.filter(
            enrollment__in=
            get_teacher_enrollments(request.user)
        ).order_by(
        '-attendance_date'
    )

    for r in records:

        ws.append([
            str(r.attendance_date),
            r.enrollment.student.roll,
            r.enrollment.student.name,
            r.enrollment.subject.name,
            r.enrollment.component,
            r.enrollment.section.name,
            r.get_status_display()
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        'attachment; filename=attendance_report.xlsx'
    )

    wb.save(response)

    return response

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

@login_required
def student_dashboard(request):

    profile = StudentProfile.objects.get(
        user=request.user
    )

    student = profile.student

    enrollments = Enrollment.objects.filter(
        student=student
    )

    records = Attendance.objects.filter(
        enrollment__in=enrollments
    ).order_by('-attendance_date')

    total = records.count()

    present = records.filter(
        status='P'
    ).count()

    percentage = 0

    if total > 0:

        percentage = round(
            (present/total)*100,
            2
        )

    return render(

        request,

        'student_dashboard.html',

        {

            'student': student,

            'records': records,

            'percentage': percentage

        }

    )

from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def clear_all_data(request):

    if not request.user.is_superuser:
        messages.error(
            request,
            "Only Super Admin can perform Factory Reset."
        )
        return redirect('dashboard')

    if request.method == 'POST':

        Attendance.objects.all().delete()

        messages.success(
            request,
            "All attendance records deleted successfully."
        )

    return redirect('dashboard')

@login_required
def promote_single_student(request):

    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':

        student_id = request.POST.get('student')
        new_semester = request.POST.get('new_semester')

        enrollments = Enrollment.objects.filter(
            student_id=student_id
        )

        total = enrollments.count()

        if total == 0:

            messages.warning(
                request,
                'No enrollments found for this student.'
            )

            return redirect('promote_single_student')

        enrollments.update(
            semester_id=new_semester
        )

        messages.success(
            request,
            f'{total} enrollment(s) updated successfully.'
        )

        return redirect('dashboard')

    return render(
        request,
        'promote_single_student.html',
        {
            'students': Student.objects.all(),
            'semesters': Semester.objects.all()
        }
    )
    
@login_required
def delete_single_student(request):

    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':

        student_id = request.POST.get('student')

        try:

            student = Student.objects.get(
                id=student_id
            )

            profile = StudentProfile.objects.filter(
                student=student
            ).first()

            if profile:
                profile.user.delete()

            student.delete()

            messages.success(
                request,
                'Student deleted successfully.'
            )

        except Exception as e:

            messages.error(
                request,
                f'Error: {str(e)}'
            )

        return redirect('dashboard')

    return render(
        request,
        'delete_single_student.html',
        {
            'students': Student.objects.all()
        }
    )
    
    
@login_required
def promote_students(request):

    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':

        old_sem = request.POST.get('old_semester')
        new_sem = request.POST.get('new_semester')

        if old_sem == new_sem:

            messages.error(
                request,
                "Old and new semesters cannot be the same."
            )

            return redirect('promote_students')

        try:

            enrollments = Enrollment.objects.filter(
                semester_id=old_sem
            )

            count = 0

            for enrollment in enrollments:

                # Check whether already promoted
                already_exists = Enrollment.objects.filter(
                    student=enrollment.student,
                    subject=enrollment.subject,
                    semester_id=new_sem,
                    section=enrollment.section,
                    component=enrollment.component
                ).exists()

                if not already_exists:

                    Enrollment.objects.create(
                        student=enrollment.student,
                        subject=enrollment.subject,
                        semester_id=new_sem,
                        section=enrollment.section,
                        component=enrollment.component
                    )

                    count += 1

            messages.success(
                request,
                f'{count} enrollments promoted successfully.'
            )

            return redirect('dashboard')

        except Exception as e:

            messages.error(
                request,
                f'Error: {str(e)}'
            )

            return redirect('promote_students')

    return render(
        request,
        'promote_students.html',
        {
            'semesters': Semester.objects.all()
        }
    )
    
    
@login_required
def promote_single_student(request):

    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':

        student_id = request.POST.get('student')
        new_semester = request.POST.get('new_semester')

        enrollments = Enrollment.objects.filter(
            student_id=student_id
        )

        total = enrollments.count()

        enrollments.update(
            semester_id=new_semester
        )

        messages.success(
            request,
            f'{total} enrollments updated successfully.'
        )

        return redirect('promote_single_student')

    return render(
        request,
        'promote_single_student.html',
        {
            'students': Student.objects.all(),
            'semesters': Semester.objects.all()
        }
    )
    
@login_required
def delete_single_student(request):

    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':

        student_id = request.POST.get('student')

        student = Student.objects.get(
            id=student_id
        )

        profile = StudentProfile.objects.get(
            student=student
        )

        profile.user.delete()

        student.delete()

        messages.success(
            request,
            'Student deleted successfully.'
        )

        return redirect('delete_single_student')

    return render(
        request,
        'delete_single_student.html',
        {
            'students': Student.objects.all()
        }
    )
    
               
@login_required
def delete_semester_students(request):

    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':

        semester_id = request.POST.get('semester')

        enrollments = Enrollment.objects.filter(
            semester_id=semester_id
        )

        student_ids = enrollments.values_list(
            'student_id',
            flat=True
        ).distinct()

        total = len(student_ids)

        Student.objects.filter(
            id__in=student_ids
        ).delete()

        messages.success(
            request,
            f'{total} students deleted successfully.'
        )

        return redirect('dashboard')

    return render(
        request,
        'delete_students.html',
        {
            'semesters': Semester.objects.all()
        }
    )
    
       
        
@login_required
def factory_reset(request):

    if not request.user.is_superuser:
        messages.error(
            request,
            "Only Super Admin can perform this action."
        )
        return redirect('dashboard')

    if request.method == 'POST':
        
        print(request.POST)

        Attendance.objects.all().delete()
        Enrollment.objects.all().delete()
        Student.objects.all().delete()
        StudentProfile.objects.all().delete()
        TeacherSubject.objects.all().delete()

        messages.success(
            request,
            "Factory reset completed successfully."
        )

    return redirect('dashboard')


from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import TeacherProfile
from .forms import TeacherProfileForm


@login_required
def edit_teacher_profile(request):

    profile, created = TeacherProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        form = TeacherProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Profile updated successfully.'
            )

            return redirect('dashboard')

    else:

        form = TeacherProfileForm(
            instance=profile
        )

    return render(
        request,
        'edit_teacher_profile.html',
        {
            'form': form,
            'profile': profile
        }
    )

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


# ==================================================
# GET TEACHER ENROLLMENTS
# ==================================================

def get_teacher_enrollments(user):

    # Super Admin can see all enrollments
    if user.is_superuser:
        return Enrollment.objects.all()

    try:
        teacher_profile = TeacherProfile.objects.get(
            user=user
        )

    except TeacherProfile.DoesNotExist:

        return Enrollment.objects.none()

    # Subjects assigned to this teacher
    assigned_subjects = TeacherSubject.objects.filter(
        teacher=teacher_profile
    ).values_list(
        'subject_id',
        flat=True
    )

    # Enrollments belonging to those subjects
    enrollments = Enrollment.objects.filter(
        subject_id__in=assigned_subjects
    )

    return enrollments.distinct()


# ==================================================
# DASHBOARD
# ==================================================

@login_required
def dashboard(request):

    # Students go to student dashboard
    if not request.user.is_staff:
        return redirect('student_dashboard')

    # Teacher Profile
    teacher_profile, created = TeacherProfile.objects.get_or_create(
        user=request.user
    )

    # ------------------------------------------------
    # SUPER ADMIN
    # ------------------------------------------------

    if request.user.is_superuser:

        student_count = Student.objects.count()

        subject_count = Subject.objects.count()

        enrollment_count = Enrollment.objects.count()

        attendance_records = Attendance.objects.all()

    # ------------------------------------------------
    # TEACHER
    # ------------------------------------------------

    else:

        allowed_enrollments = get_teacher_enrollments(
            request.user
        )

        student_count = Student.objects.filter(
            enrollment__in=allowed_enrollments
        ).distinct().count()

        subject_count = TeacherSubject.objects.filter(
            teacher=teacher_profile
        ).count()

        enrollment_count = allowed_enrollments.count()

        attendance_records = Attendance.objects.filter(
            enrollment__in=allowed_enrollments
        )

    # ------------------------------------------------
    # ATTENDANCE COUNTS
    # (supports double periods)
    # ------------------------------------------------

    attendance_count = sum(
        record.period_count
        for record in attendance_records
    )

    present_count = sum(
        record.period_count
        for record in attendance_records
        if record.status == 'P'
    )

    absent_count = sum(
        record.period_count
        for record in attendance_records
        if record.status == 'A'
    )

    # ------------------------------------------------
    # CONTEXT
    # ------------------------------------------------

    context = {

        'teacher_profile': teacher_profile,

        'student_count': student_count,

        'subject_count': subject_count,

        'enrollment_count': enrollment_count,

        'attendance_count': attendance_count,

        'present_count': present_count,

        'absent_count': absent_count,
    }

    return render(
        request,
        'dashboard.html',
        context
    )