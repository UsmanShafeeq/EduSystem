from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile,
    Department,
    Program,
    Course,
    Student,
    Designation,
    Staff,
    Admission,
    Enrollment,
    Attendance,
    Exam,
    Grade,
    Fee,
    Notification,
)
from datetime import date

# ============================================================
# 1. USER SERIALIZER + USER PROFILE (Nested & CRUD-ready)
# ============================================================

class UserSerializer(serializers.ModelSerializer):
    """Read-only serializer for Django User."""
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_staff", "is_superuser"]

class UserCreateSerializer(serializers.ModelSerializer):
    """Create User + automatically generate UserProfile with role."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password", "is_staff", "is_superuser"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # Auto-create UserProfile
        UserProfile.objects.create(
            user=user,
            role="Admin" if user.is_superuser else "Staff" if user.is_staff else "Student"
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only nested user profile."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "role"]

# ============================================================
# 2. DEPARTMENT, PROGRAM, COURSE (Hyperlinked + Nested)
# ============================================================

class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    """Include related programs as hyperlinks."""
    programs = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="program-detail"  # Ensure your viewsets have 'program-detail' name
    )

    class Meta:
        model = Department
        fields = ["id", "name", "code", "description", "hod", "programs"]
        extra_kwargs = {
            'hod': {'view_name': 'staff-detail', 'lookup_field': 'pk'}
        }

class ProgramSerializer(serializers.HyperlinkedModelSerializer):
    """Nested department + related courses as hyperlinks."""
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True
    )
    courses = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="course-detail"
    )

    class Meta:
        model = Program
        fields = [
            "id", "program_number", "name", "code", "program_type",
            "duration_years", "description", "department", "department_id", "courses"
        ]

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    program = ProgramSerializer(read_only=True)
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), source="program", write_only=True
    )

    class Meta:
        model = Course
        fields = ["id", "code", "title", "credit_hours", "semester", "program", "program_id"]

# ============================================================
# 3. STUDENT MANAGEMENT (Nested + validations)
# ============================================================

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    program = ProgramSerializer(read_only=True)
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), source="program", write_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id", "registration_no", "user", "full_name", "gender", "dob",
            "email", "phone", "address", "program", "program_id",
            "enrollment_year", "is_active", "photo", "age"
        ]

    def validate_dob(self, value):
        """DOB cannot be in the future."""
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

class StudentCreateSerializer(serializers.ModelSerializer):
    """Separate serializer for creating student with existing user."""
    class Meta:
        model = Student
        fields = [
            "id", "user", "registration_no", "full_name", "gender", "dob",
            "email", "phone", "address", "program", "enrollment_year", "photo"
        ]

# ============================================================
# 4. STAFF MANAGEMENT
# ============================================================

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = "__all__"

class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    designation = DesignationSerializer(read_only=True)
    designation_id = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(), source="designation", write_only=True
    )
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True
    )

    class Meta:
        model = Staff
        fields = [
            "id", "user", "full_name", "staff_type", "designation",
            "designation_id", "department", "department_id",
            "email", "phone", "date_joined", "photo", "is_active"
        ]

class StaffCreateSerializer(serializers.ModelSerializer):
    """Create staff with existing user"""
    class Meta:
        model = Staff
        fields = [
            "id", "user", "full_name", "staff_type", "designation", "department",
            "email", "phone", "photo"
        ]

# ============================================================
# 5. ADMISSIONS & ENROLLMENT (Validation + nested)
# ============================================================

class AdmissionSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source="student", write_only=True)
    program = ProgramSerializer(read_only=True)
    program_id = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), source="program", write_only=True)

    class Meta:
        model = Admission
        fields = ["id", "student", "student_id", "program", "program_id", "admission_date", "status"]

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source="student", write_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source="course", write_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "student_id", "course", "course_id", "semester", "year", "date_enrolled"]

    def validate(self, data):
        """Prevent duplicate enrollment for same student/course/semester/year"""
        if Enrollment.objects.filter(
            student=data["student"], course=data["course"],
            semester=data["semester"], year=data["year"]
        ).exists():
            raise serializers.ValidationError("This student is already enrolled in this course for this semester/year.")
        return data

# ============================================================
# 6. ATTENDANCE & EXAMS
# ============================================================

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source="student", write_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source="course", write_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "student", "student_id", "course", "course_id", "date", "status"]

    def validate(self, data):
        """Unique attendance per student/course/date"""
        if Attendance.objects.filter(
            student=data["student"], course=data["course"], date=data["date"]
        ).exists():
            raise serializers.ValidationError("Attendance already exists for this student/course/date.")
        return data

class ExamSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source="course", write_only=True)

    class Meta:
        model = Exam
        fields = ["id", "course", "course_id", "exam_type", "date", "total_marks"]

class GradeSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source="student", write_only=True)
    exam = ExamSerializer(read_only=True)
    exam_id = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all(), source="exam", write_only=True)

    class Meta:
        model = Grade
        fields = ["id", "student", "student_id", "exam", "exam_id", "obtained_marks"]

    def validate_obtained_marks(self, value):
        if value < 0:
            raise serializers.ValidationError("Marks cannot be negative")
        return value

# ============================================================
# 7. FEES & PAYMENTS
# ============================================================

class FeeSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source="student", write_only=True)

    class Meta:
        model = Fee
        fields = ["id", "student", "student_id", "amount", "due_date", "is_paid", "payment_date", "status"]
        read_only_fields = ["status"]

    @property
    def is_overdue(self):
        return not self.is_paid and self.due_date < date.today()

# ============================================================
# 8. NOTIFICATIONS
# ============================================================

class NotificationSerializer(serializers.ModelSerializer):
    recipient_student = StudentSerializer(read_only=True)
    recipient_student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source="recipient_student", write_only=True, required=False
    )
    recipient_staff = StaffSerializer(read_only=True)
    recipient_staff_id = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(), source="recipient_staff", write_only=True, required=False
    )

    class Meta:
        model = Notification
        fields = [
            "id", "recipient_student", "recipient_student_id",
            "recipient_staff", "recipient_staff_id",
            "notif_type", "title", "message", "created_at",
            "read", "auto_resolved"
        ]
