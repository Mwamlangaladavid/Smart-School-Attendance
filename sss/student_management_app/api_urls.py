from django.urls import path
from . import api_views

urlpatterns = [
    # Test connection
    path('test/', api_views.api_test_connection, name='api_test_connection'),
    
    # Multiple login endpoints for compatibility
    path('login/', api_views.api_mobile_login, name='api_login'),
    path('auth/login/', api_views.api_mobile_login, name='api_auth_login'),
    path('mobile/login/', api_views.api_mobile_login, name='api_mobile_login_alt'),
    path('user/login/', api_views.api_mobile_login, name='api_user_login'),
    
    # User type specific login endpoints
    path('hod/login/', api_views.api_mobile_login, name='api_hod_login'),
    path('staff/login/', api_views.api_mobile_login, name='api_staff_login'),
    path('student/login/', api_views.api_mobile_login, name='api_student_login'),
    path('parent/login/', api_views.api_mobile_login, name='api_parent_login'),
    
    # Dashboard endpoints
    path('hod/dashboard/', api_views.api_hod_dashboard, name='api_hod_dashboard'),
    path('staff/dashboard/', api_views.api_staff_dashboard, name='api_staff_dashboard'),
    path('parent/dashboard/', api_views.api_parent_dashboard, name='api_parent_dashboard'),
    
    # Staff management
    path('staff/', api_views.api_get_all_staff, name='api_get_all_staff'),
    path('staff/add/', api_views.api_add_staff, name='api_add_staff'),
    
    # Student management
    path('students/', api_views.api_get_all_students, name='api_get_all_students'),
    path('students/add/', api_views.api_add_student, name='api_add_student'),
    
    # Leave requests
    path('leave-requests/', api_views.api_get_leave_requests, name='api_get_leave_requests'),
    path('leave-requests/update/', api_views.api_update_leave_request, name='api_update_leave_request'),
    
    #Staff endpoints
    path('staff/dashboard/', api_views.api_staff_dashboard, name='api_staff_dashboard'),

    #academic year endpoints
    path('academic-years/', api_views.api_get_academic_years, name='api_get_academic_years'),
    path('academic-years/add/', api_views.api_add_academic_year, name='api_add_academic_year'),

    # Parent endpoints
    path('parent/children/', api_views.api_parent_children, name='api_parent_children'),
    path('parent/apply-leave/', api_views.api_parent_apply_leave, name='api_parent_apply_leave'),
    path('parent/leave-history/', api_views.api_parent_leave_history, name='api_parent_leave_history'),
    path('parent/attendance/', api_views.api_parent_attendance, name='api_parent_attendance'),
    path('parent/notifications/', api_views.api_parent_notifications, name='api_parent_notifications'),
    path('notifications/mark-read/', api_views.api_mark_notification_read, name='api_mark_notification_read'),
    path('notifications/mark-all-read/', api_views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),
    path('notifications/delete/<int:notification_id>/', api_views.api_delete_notification, name='api_delete_notification'),
]   
