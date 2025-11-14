from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Department,
    Program,
    Course,
    Student,
    Staff,
    Designation,
    Admission,
    Enrollment,
    Attendance,
    Exam,
    Grade,
    Fee,
    Notification,
)


# ============================================================
# 1. DEPARTMENT, PROGRAM, COURSE STRUCTURE
# ============================================================
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "hod")
    search_fields = ("name", "code")
    list_filter = ("hod",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = (
        "program_number",
        "name",
        "code",
        "program_type",
        "department",
        "duration_years",
    )
    search_fields = ("name", "code")
    list_filter = ("program_type", "department")
    ordering = ("program_number",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "program", "semester", "credit_hours")
    search_fields = ("code", "title", "program__code")
    list_filter = ("program", "semester")


# ============================================================
# 2. STUDENT MANAGEMENT
# ============================================================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "registration_no",
        "full_name",
        "gender",
        "program",
        "enrollment_year",
        "is_active",
    )
    search_fields = ("registration_no", "full_name", "email", "phone")
    list_filter = ("program", "gender", "enrollment_year", "is_active")


# ============================================================
# 3. STAFF MANAGEMENT
# ============================================================
@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "staff_type",
        "designation",
        "department",
        "email",
        "phone",
        "is_active",
    )
    search_fields = ("full_name", "email", "phone")
    list_filter = ("staff_type", "designation", "department", "is_active")


# ============================================================
# 4. ADMISSIONS & ENROLLMENT
# ============================================================
@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "program", "admission_date", "status")
    search_fields = ("student__full_name", "program__name")
    list_filter = ("status", "program")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "semester", "year", "date_enrolled")
    search_fields = ("student__full_name", "course__code")
    list_filter = ("semester", "year", "course")


# ============================================================
# 5. ATTENDANCE & EXAMS
# ============================================================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "date", "status")
    search_fields = ("student__full_name", "course__code")
    list_filter = ("status", "course")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("course", "exam_type", "date", "total_marks")
    search_fields = ("course__code", "exam_type")
    list_filter = ("exam_type", "course")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "obtained_marks")
    search_fields = ("student__full_name", "exam__course__code")
    list_filter = ("exam",)


# ============================================================
# 6. FEES & PAYMENTS
# ============================================================
@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ("student", "amount", "due_date", "is_paid", "payment_date")
    search_fields = ("student__full_name",)
    list_filter = ("is_paid",)


# ============================================================
# 6. Notification
# ============================================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "notif_type",
        "title_display",
        "recipient_student",
        "recipient_staff",
        "created_at",
        "read",
        "auto_resolved",
    )
    list_filter = ("notif_type", "read", "auto_resolved", "created_at")
    search_fields = (
        "title",
        "message",
        "recipient_student__full_name",
        "recipient_staff__full_name",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 20

    # Bold unread notifications & highlight auto-resolved in green
    def title_display(self, obj):
        if not obj.read:
            return format_html("<b>{}</b>", obj.title)
        elif obj.auto_resolved:
            return format_html("<span style='color:green'>{}</span>", obj.title)
        return obj.title

    title_display.short_description = "Title"

    # Auto-refresh changelist every 10 seconds (optional)
    change_list_template = "admin/notifications_changelist.html"