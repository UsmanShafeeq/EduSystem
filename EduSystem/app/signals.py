from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from .models import (
    Admission,
    Enrollment,
    Fee,
    Exam,
    Attendance,
    Grade,
    Staff,
    Notification,
)

# ============================================================
# 1. ADMISSION NOTIFICATIONS
# ============================================================
@receiver(post_save, sender=Admission)
def create_admission_notification(sender, instance, created, **kwargs):
    """
    Notify students when their admission is created or updated.
    """
    notif_type = "Admission" if created else "Admission Update"
    Notification.objects.create(
        recipient_student=instance.student,
        notif_type=notif_type,
        title=f"Admission {'Created' if created else 'Updated'}",
        message=f"Your admission for {instance.program.name} has been "
                f"{'created' if created else 'updated'} with status {instance.status}.",
    )


# ============================================================
# 2. ENROLLMENT NOTIFICATIONS
# ============================================================
@receiver(post_save, sender=Enrollment)
def create_enrollment_notification(sender, instance, created, **kwargs):
    """
    Notify students upon successful course enrollment.
    """
    if created:
        Notification.objects.create(
            recipient_student=instance.student,
            notif_type="Enrollment",
            title="Course Enrollment Successful",
            message=f"You have been enrolled in {instance.course.code} "
                    f"for Semester {instance.semester} ({instance.year}).",
        )


# ============================================================
# 3. FEE NOTIFICATIONS
# ============================================================
@receiver(post_save, sender=Fee)
def create_fee_notification(sender, instance, created, **kwargs):
    """
    Notify students about fee creation, overdue, and payment.
    """
    if created and not instance.is_paid:
        # New fee assigned
        Notification.objects.create(
            recipient_student=instance.student,
            notif_type="Fee",
            title="New Fee Assigned",
            message=f"A new fee of {instance.amount} is due on {instance.due_date}.",
        )
    elif not created and not instance.is_paid and instance.due_date < date.today():
        # Overdue fee
        Notification.objects.create(
            recipient_student=instance.student,
            notif_type="Fee",
            title="Fee Overdue",
            message=f"Your fee of {instance.amount} is overdue!",
        )
    elif not created and instance.is_paid:
        # Auto-resolve previous fee notifications
        Notification.objects.filter(
            recipient_student=instance.student, notif_type="Fee", read=False
        ).update(read=True, auto_resolved=True)

        Notification.objects.create(
            recipient_student=instance.student,
            notif_type="Fee",
            title="Fee Paid",
            message=f"Your fee of {instance.amount} has been paid.",
            read=True,
            auto_resolved=True,
        )


# ============================================================
# 4. EXAM NOTIFICATIONS
# ============================================================
@receiver(post_save, sender=Exam)
def create_exam_notification(sender, instance, created, **kwargs):
    """
    Notify all students of a program when a new exam is scheduled.
    """
    if created:
        students = instance.course.program.students.all()
        for student in students:
            Notification.objects.create(
                recipient_student=student,
                notif_type="Exam",
                title="New Exam Scheduled",
                message=f"The {instance.exam_type} exam for {instance.course.title} "
                        f"is scheduled on {instance.date}.",
            )


# ============================================================
# 5. ATTENDANCE NOTIFICATIONS
# ============================================================
@receiver(post_save, sender=Attendance)
def create_attendance_notification(sender, instance, created, **kwargs):
    """
    Notify students when their attendance is recorded.
    """
    if created:
        Notification.objects.create(
            recipient_student=instance.student,
            notif_type="Attendance",
            title="Attendance Recorded",
            message=f"Your attendance for {instance.course.code} "
                    f"on {instance.date} has been marked as {instance.status}.",
        )


# ============================================================
# 6. GRADE NOTIFICATIONS
# ============================================================
@receiver(post_save, sender=Grade)
def create_grade_notification(sender, instance, created, **kwargs):
    """
    Notify students when a grade is posted.
    """
    if created:
        Notification.objects.create(
            recipient_student=instance.student,
            notif_type="Grade",
            title=f"{instance.exam.exam_type} Exam Results",
            message=f"You scored {instance.obtained_marks} in {instance.exam.course.title}.",
        )


# ============================================================
# 7. STAFF NOTIFICATIONS
# ============================================================
@receiver(post_save, sender=Staff)
def create_staff_notification(sender, instance, created, **kwargs):
    """
    Notify staff on creation or record update.
    """
    if created:
        Notification.objects.create(
            recipient_staff=instance,
            notif_type="Staff",
            title="Welcome to Staff",
            message=f"Welcome {instance.full_name} to "
                    f"{instance.department.name if instance.department else 'the institution'}.",
        )
    else:
        Notification.objects.create(
            recipient_staff=instance,
            notif_type="Staff",
            title="Staff Record Updated",
            message="Your staff record has been updated.",
        )
