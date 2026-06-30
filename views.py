from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date

from .models import Enrollment, Attendance


def take_attendance(request):

    enrollments = Enrollment.objects.all()

    if request.method == 'POST':

        for e in enrollments:

            status = request.POST.get(
                f"status_{e.id}"
            )

            Attendance.objects.update_or_create(
                enrollment=e,
                attendance_date=date.today(),

                defaults={
                    'status': status
                }
            )

        messages.success(
            request,
            "Attendance saved successfully."
        )

        return redirect('take_attendance')

    return render(
        request,
        'attendance_form.html',
        {'enrollments': enrollments}
    )