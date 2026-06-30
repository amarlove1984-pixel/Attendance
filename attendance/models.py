from django.db import models
from django.contrib.auth.models import User


# ==================================================
# SEMESTER
# ==================================================

class Semester(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# ==================================================
# PAPER (formerly Section)
# ==================================================

class Section(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Paper"
        verbose_name_plural = "Papers"

    def __str__(self):
        return self.name


# ==================================================
# SUBJECT
# ==================================================

class Subject(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


# ==================================================
# STUDENT
# ==================================================

class Student(models.Model):

    roll = models.CharField(
        max_length=30,
        unique=True
    )

    registration_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    name = models.CharField(
        max_length=120
    )

    def __str__(self):
        return f"{self.roll} - {self.name}"


# ==================================================
# ENROLLMENT
# ==================================================

class Enrollment(models.Model):

    COMPONENT_CHOICES = [
        ('Theory', 'Theory'),
        ('Tutorial', 'Tutorial'),
        ('Practical', 'Practical'),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        verbose_name='Paper'
    )

    component = models.CharField(
        max_length=20,
        choices=COMPONENT_CHOICES
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (
            'student',
            'semester',
            'section',
            'subject',
            'component'
        )

    def __str__(self):
        return (
            f"{self.student} | "
            f"{self.subject} | "
            f"{self.section} | "
            f"{self.component}"
        )


# ==================================================
# ATTENDANCE
# ==================================================

class Attendance(models.Model):

    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
    ]

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    attendance_date = models.DateField()

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='P'
    )

    # NEW FIELD
    period_count = models.PositiveIntegerField(
        default=1
    )

    class Meta:

        # Only keep this when multiple attendance
        # on same day is NOT allowed.


        def __str__(self):

            return (
                f"{self.enrollment.student.name} | "
                f"{self.attendance_date} | "
                f"{self.status} | "
                f"{self.period_count} Period(s)"
            )

# ==================================================
# TEACHER PROFILE
# ==================================================

from django.db import models
from django.contrib.auth.models import User


class TeacherProfile(models.Model):

    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    employee_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    photo = models.ImageField(
        upload_to='teacher_photos/',
        blank=True,
        null=True
    )

    designation = models.CharField(
        max_length=100,
        blank=True
    )

    department = models.CharField(
        max_length=100,
        blank=True
    )
    
    email = models.EmailField(
        blank=True
    )

    joining_date = models.DateField(
        blank=True,
        null=True
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUPS,
        blank=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    qualification = models.CharField(
        max_length=200,
        blank=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    emergency_contact = models.CharField(
        max_length=15,
        blank=True
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

# ==================================================
# TEACHER SUBJECT
# ==================================================

class TeacherSubject(models.Model):

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.teacher} - {self.subject}"


# ==================================================
# STUDENT PROFILE
# ==================================================
from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):

    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students',
        limit_choices_to={'is_staff': True}
    )

    photo = models.ImageField(
        upload_to='student_photos/',
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    email = models.EmailField(blank=True)

    address = models.TextField(blank=True)

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUPS,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    guardian_name = models.CharField(
        max_length=100,
        blank=True
    )

    guardian_phone = models.CharField(
        max_length=15,
        blank=True
    )

    emergency_contact = models.CharField(
        max_length=15,
        blank=True
    )

    def __str__(self):
        return self.student.name
    
# ==================================================
# TIMETABLE
# ==================================================

class Timetable(models.Model):

    DAYS = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
    ]

    day = models.CharField(
        max_length=10,
        choices=DAYS
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        verbose_name='Paper'
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    room = models.CharField(
        max_length=30
    )

    def __str__(self):
        return (
            f"{self.day} | "
            f"{self.subject.name}"
        )
        
