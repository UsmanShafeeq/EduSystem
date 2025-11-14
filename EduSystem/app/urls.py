from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'designations', views.DesignationViewSet)
router.register(r'programs', views.ProgramViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'staff', views.StaffViewSet)
router.register(r'admissions', views.AdmissionViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'exams', views.ExamViewSet)
router.register(r'grades', views.GradeViewSet)
router.register(r'fees', views.FeeViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Bulk APIs
    path('students/bulk/', views.StudentBulkAPIView.as_view(), name='student-bulk'),
    path('courses/bulk/', views.CourseBulkAPIView.as_view(), name='course-bulk'),

    # Dashboard
    path('dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
]
