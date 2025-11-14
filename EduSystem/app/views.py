from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from datetime import date, timedelta
from django.db import transaction

from .models import (
    Department, Program, Course, Designation,
    Student, Staff, Admission, Enrollment,
    Attendance, Exam, Grade, Fee, Notification,
    RoleBasedPermission
)
from .serializers import (
    DepartmentSerializer, ProgramSerializer, CourseSerializer, DesignationSerializer,
    StudentSerializer, StaffSerializer, AdmissionSerializer, EnrollmentSerializer,
    AttendanceSerializer, ExamSerializer, GradeSerializer, FeeSerializer, NotificationSerializer
)


# ============================================================
# 1. Pagination
# ============================================================
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# ============================================================
# 2. Dashboard API
# ============================================================
class DashboardAPIView(APIView):
    """
    Admin & Staff Dashboard for overall statistics.
    Supports filters: today, week, month, custom (?start=YYYY-MM-DD&end=YYYY-MM-DD)
    """
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff"]

    def get(self, request):
        filter_type = request.query_params.get("filter")
        start_date = request.query_params.get("start")
        end_date = request.query_params.get("end")
        start = end = None

        if filter_type == "today":
            start = now().date()
            end = start + timedelta(days=1)
        elif filter_type == "week":
            start = now().date() - timedelta(days=7)
            end = now().date() + timedelta(days=1)
        elif filter_type == "month":
            start = now().replace(day=1).date()
            end = now().date() + timedelta(days=1)
        elif filter_type == "custom" and start_date and end_date:
            from datetime import datetime
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date() + timedelta(days=1)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        def date_filter(model):
            if hasattr(model, "created_at") and start and end:
                return model.objects.filter(created_at__range=[start, end])
            return model.objects.all()

        data = {
            "total_students": date_filter(Student).count(),
            "total_staff": date_filter(Staff).count(),
            "total_admissions": date_filter(Admission).count(),
            "total_enrollments": date_filter(Enrollment).count(),
            "total_attendance": date_filter(Attendance).count(),
            "total_exams": date_filter(Exam).count(),
            "total_grades": date_filter(Grade).count(),
            "total_fees": date_filter(Fee).count(),
            "total_notifications": date_filter(Notification).count(),
            "filter_info": {
                "filter_type": filter_type or "all",
                "start_date": str(start) if start else None,
                "end_date": str(end) if end else None,
            },
        }
        return Response(data, status=status.HTTP_200_OK)


# ============================================================
# 3. Department, Designation, Program, Course ViewSets
# ============================================================
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["code", "name"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    pagination_class = StandardResultsSetPagination


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all().order_by("title")
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["title"]
    search_fields = ["title"]
    ordering_fields = ["title"]
    pagination_class = StandardResultsSetPagination


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all().order_by("program_number")
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department", "program_type", "code"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "program_number"]
    pagination_class = StandardResultsSetPagination


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("code")
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["program", "semester", "code"]
    search_fields = ["title", "code"]
    ordering_fields = ["title", "code"]
    pagination_class = StandardResultsSetPagination


# ============================================================
# 4. Student & Staff ViewSets
# ============================================================
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by("-id")
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff", "Student"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["program", "is_active", "enrollment_year"]
    search_fields = ["full_name", "registration_no", "email"]
    ordering_fields = ["full_name", "enrollment_year", "id"]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, "role", None)
        if role == "Student":
            return Student.objects.filter(user=user)
        elif role == "Staff":
            return Student.objects.all()
        return super().get_queryset()

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        student = self.get_object()
        student.is_active = False
        student.save()
        return Response({"status": "Student deactivated"})


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department", "staff_type", "is_active"]
    search_fields = ["full_name", "email"]
    ordering_fields = ["full_name", "id"]
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        staff = self.get_object()
        staff.is_active = False
        staff.save()
        return Response({"status": "Staff deactivated"})


# ============================================================
# 5. Admission, Enrollment, Attendance, Exam, Grade, Fee, Notification
# ============================================================
class AdmissionViewSet(viewsets.ModelViewSet):
    queryset = Admission.objects.all()
    serializer_class = AdmissionSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "program", "student"]
    search_fields = ["student__full_name", "program__name"]
    ordering_fields = ["id", "admission_date"]
    pagination_class = StandardResultsSetPagination


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff", "Student"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "course", "semester", "year"]
    search_fields = ["student__full_name", "course__title"]
    ordering_fields = ["id", "year", "semester"]
    pagination_class = StandardResultsSetPagination


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "course", "date", "status"]
    search_fields = ["student__full_name", "course__title"]
    ordering_fields = ["date", "student"]
    pagination_class = StandardResultsSetPagination


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["course", "exam_type", "date"]
    search_fields = ["course__title"]
    ordering_fields = ["date"]
    pagination_class = StandardResultsSetPagination


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff", "Student"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "exam"]
    search_fields = ["student__full_name", "exam__course__title"]
    ordering_fields = ["id"]
    pagination_class = StandardResultsSetPagination


class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff", "Student"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "is_paid"]
    search_fields = ["student__full_name"]
    ordering_fields = ["payment_date", "amount"]
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        fee = self.get_object()
        fee.is_paid = True
        fee.payment_date = date.today()
        fee.save()
        return Response({"status": "Fee marked as paid"})


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["Admin", "Staff", "Student"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["recipient_student", "recipient_staff", "notif_type", "read"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at"]
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({"status": "Notification marked as read"})


# ============================================================
# 6. Bulk Create / Update Students & Courses
# ============================================================
class StudentBulkAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        """Bulk Create Students"""
        serializer = StudentSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Students created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request):
        """Bulk Update Students"""
        updated = []
        for item in request.data:
            student_id = item.get("id")
            if not student_id:
                continue
            try:
                student = Student.objects.get(id=student_id)
                serializer = StudentSerializer(student, data=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated.append(serializer.data)
            except Student.DoesNotExist:
                continue
        return Response({"message": "Students updated successfully", "data": updated}, status=status.HTTP_200_OK)


class CourseBulkAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        """Bulk Create Courses"""
        serializer = CourseSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Courses created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request):
        """Bulk Update Courses"""
        updated = []
        for item in request.data:
            course_id = item.get("id")
            if not course_id:
                continue
            try:
                course = Course.objects.get(id=course_id)
                serializer = CourseSerializer(course, data=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated.append(serializer.data)
            except Course.DoesNotExist:
                continue
        return Response({"message": "Courses updated successfully", "data": updated}, status=status.HTTP_200_OK)
