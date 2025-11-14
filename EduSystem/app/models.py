from django.db import models
from django.contrib.auth.models import User
from datetime import date
from rest_framework.permissions import BasePermission
from django.db.models.signals import post_save
from django.dispatch import receiver


# ============================================================
# 0. ROLE-BASED AUTHENTICATION MODELS
# ============================================================

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Staff', 'Staff'),
        ('Student', 'Student'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Auto-create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            role = "Admin"
        elif instance.is_staff:
            role = "Staff"
        else:
            role = "Student"
        UserProfile.objects.create(user=instance, role=role)


# ============================================================
# 1. CUSTOM PERMISSIONS (ROLE BASED)
# ============================================================

class IsAdmin(BasePermission):
    """Allow access only to admin/superusers."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or
            getattr(request.user.profile, 'role', None) == 'Admin'
        )


class IsStaff(BasePermission):
    """Allow access only to staff users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or
            getattr(request.user.profile, 'role', None) == 'Staff'
        )


class IsStudent(BasePermission):
    """Allow access only to students."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            getattr(request.user.profile, 'role', None) == 'Student'
        )


class RoleBasedPermission(BasePermission):
    """
    Generic flexible role-based permission.
    Define `allowed_roles = ['Admin', 'Staff']` inside your ViewSet.
    """
    def has_permission(self, request, view):
        allowed_roles = getattr(view, 'allowed_roles', [])
        if not request.user.is_authenticated:
            return False
        role = getattr(request.user.profile, 'role', None)
        return role in allowed_roles


# ============================================================
# 2. DEPARTMENT, PROGRAM, COURSE STRUCTURE
# ============================================================

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    hod = models.ForeignKey(
        "Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="headed_department"
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class Program(models.Model):
    PROGRAM_TYPES = [
        ("BS", "Bachelor"),
        ("MS", "Master"),
        ("PhD", "Doctorate"),
        ("Diploma", "Diploma"),
    ]

    program_number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="programs"
    )
    duration_years = models.PositiveIntegerField(default=4)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["program_number"]

    def __str__(self):
        return f"{self.program_number}. {self.name} ({self.code})"


class Course(models.Model):
    SEMESTERS = [(i, f"Semester {i}") for i in range(1, 9)]

    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=150)
    credit_hours = models.DecimalField(max_digits=3, decimal_places=1)
    semester = models.PositiveIntegerField(choices=SEMESTERS)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="courses"
    )

    @property
    def short_name(self):
        return self.code

    @property
    def program_code(self):
        return self.program.code

    @property
    def credit_info(self):
        return f"{self.code} ({self.credit_hours} Cr)"

    def __str__(self):
        return f"{self.program.code} - {self.code}"


# ============================================================
# 3. STUDENT MANAGEMENT
# ============================================================

class Student(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    registration_no = models.CharField(max_length=30, unique=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )
    full_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="students"
    )
    enrollment_year = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to="students/photos/", blank=True, null=True)

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    def __str__(self):
        return f"{self.full_name} ({self.registration_no})"


# ============================================================
# 4. STAFF MANAGEMENT
# ============================================================

class Designation(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Staff(models.Model):
    STAFF_TYPE = [
        ("Teaching", "Teaching"),
        ("Non-Teaching", "Non-Teaching"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="staff_profile"
    )
    full_name = models.CharField(max_length=150)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPE)
    designation = models.ForeignKey(
        Designation, on_delete=models.SET_NULL, null=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    date_joined = models.DateField(auto_now_add=True)
    photo = models.ImageField(upload_to="staff/photos/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name} ({self.designation})"


# ============================================================
# 5. ADMISSIONS & ENROLLMENT
# ============================================================

class Admission(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="admission"
    )
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    admission_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"Admission: {self.student.full_name} - {self.status}"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    date_enrolled = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course", "semester", "year")

    def __str__(self):
        return f"{self.student.full_name} - {self.course.code} - Sem {self.semester}"


# ============================================================
# 6. ATTENDANCE & EXAMS
# ============================================================

class Attendance(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Leave", "Leave"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("student", "course", "date")

    def __str__(self):
        return f"{self.student.full_name} - {self.course.code} - {self.status}"


class Exam(models.Model):
    EXAM_TYPE = [
        ("Midterm", "Midterm"),
        ("Final", "Final"),
        ("Quiz", "Quiz"),
        ("Assignment", "Assignment"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE)
    date = models.DateField()
    total_marks = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.course.title} - {self.exam_type}"


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.student.full_name} - {self.exam.course.code}"


# ============================================================
# 7. FEES & PAYMENTS
# ============================================================

class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(blank=True, null=True)

    @property
    def status(self):
        return "Paid" if self.is_paid else "Unpaid"

    def __str__(self):
        return f"{self.student.full_name} - {self.status}"


# ============================================================
# 8. NOTIFICATIONS
# ============================================================

class Notification(models.Model):
    recipient_student = models.ForeignKey("Student", on_delete=models.CASCADE, blank=True, null=True)
    recipient_staff = models.ForeignKey("Staff", on_delete=models.CASCADE, blank=True, null=True)
    notif_type = models.CharField(max_length=50)
    title = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    auto_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.notif_type}: {self.title}"
