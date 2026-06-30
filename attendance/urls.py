from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .forms import CustomPasswordResetForm


urlpatterns = [

    path('', views.teacher_login, name='login'),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'attendance/',
        views.take_attendance,
        name='take_attendance'
    ),

    path(
        'report/',
        views.attendance_report,
        name='attendance_report'
    ),

    path(
        'percentage/',
        views.percentage_report,
        name='percentage_report'
    ),

    path(
        'delete-single-student/',
        views.delete_single_student,
        name='delete_single_student'
    ),
    
    path(
        'defaulters/',
        views.defaulter_report,
        name='defaulter_report'
    ),

    path(
        'history/',
        views.student_history,
        name='student_history'
    ),

    path(
        'edit-attendance/',
        views.edit_attendance,
        name='edit_attendance'
    ),

    path(
        'export-excel/',
        views.export_excel,
        name='export_excel'
    ),

    path(
        'export-pdf/',
        views.export_pdf,
        name='export_pdf'
    ),

    path(
        'change-password/',
        views.change_password,
        name='change_password'
    ),

    path(
        'profile/',
        views.profile,
        name='profile'
    ),

    path(
        'logout/',
        views.teacher_logout,
        name='logout'
    ),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            form_class=CustomPasswordResetForm
        ),
        name='password_reset'
    ),
    path(
        'clear-data/',
        views.clear_all_data,
        name='clear_all_data'
    ),
    
    path(
        'promote-students/',
        views.promote_students,
        name='promote_students'
    ),

    path(
        'delete-semester-students/',
        views.delete_semester_students,
        name='delete_semester_students'
    ),

    path(
        'factory-reset/',
        views.factory_reset,
        name='factory_reset'
    ),
    path(
        'promote-single-student/',
        views.promote_single_student,
        name='promote_single_student'
    ),

    path(
        'delete-single-student/',
        views.delete_single_student,
        name='delete_single_student'
    ),
    path(
        'promote-single-student/',
        views.promote_single_student,
        name='promote_single_student'
    ),
    path(
        'upload-students/',
        views.upload_students,
        name='upload_students'
    ),
    path(
        'delete-single-student/',
        views.delete_single_student,
        name='delete_single_student'
    ),
    
    path(
        'edit-teacher-profile/',
        views.edit_teacher_profile,
        name='edit_teacher_profile'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    path(
        'student-dashboard/',
        views.student_dashboard,
        name='student_dashboard'
    ),
    
    path(
    'analytics/',
    views.analytics_dashboard,
    name='analytics_dashboard'
    ),
    
    path(
    'analytics/',
    views.analytics_dashboard,
    name='analytics_dashboard'
    ),
    
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )