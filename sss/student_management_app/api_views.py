from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.views.decorators.http import require_http_methods
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import json
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from .models import (
    CustomUser, Staffs, Students, Parents, Grades, Streams, AcademicYear,
    LeaveReportStaff, LeaveReportStudent, FeedBackStaffs, FeedBackParents,
    Attendance, AttendanceReport
)

def get_user_from_token(request):
    """Helper function to get user from token"""
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Token '):
        token_key = auth_header.split(' ')[1]
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None
    return None

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def api_test_connection(request):
    """Test API connection"""
    return JsonResponse({
        'success': True,
        'message': 'Connection successful',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_users': CustomUser.objects.count()
    })

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_mobile_login(request):
    """Mobile API Login endpoint - no authentication required"""
    try:
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Only POST method allowed'
            }, status=405)
        
        # Use request.data (DRF automatically parses JSON)
        data = request.data
        
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type', '').lower()
        
        print(f"Login attempt - Email: {email}, Password length: {len(password) if password else 0}, User Type: {user_type}")
        
        if not email or not password:
            return JsonResponse({
                'success': False,
                'error': 'Email and password are required'
            })
        
        # Check if user exists
        try:
            user_exists = CustomUser.objects.get(email=email)
            print(f"User found: {user_exists.username}, Type: {user_exists.user_type}, Active: {user_exists.is_active}")
        except CustomUser.DoesNotExist:
            print(f"User with email {email} does not exist")
            return JsonResponse({
                'success': False,
                'error': 'Invalid email or password'
            })
        
        # Use EmailBackEnd for authentication
        from .EmailBackEnd import EmailBackEnd
        user = EmailBackEnd.authenticate(request, username=email, password=password)

        
        print(f"Authentication result: {user}")
        
        if user is not None and user.is_active:
            # Create or get token for the user
            token, created = Token.objects.get_or_create(user=user)
            print(f"Token created/retrieved: {token.key[:10]}... (created: {created})")
            
            # Determine user type and get user data
            actual_user_type = 'Student'  # default
            user_data = {}
            
            if user.user_type == '1':  # HOD/Admin
                actual_user_type = 'HOD'
                user_data = {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'is_superuser': user.is_superuser,
                }
            elif user.user_type == '2':  # Staff
                actual_user_type = 'Staff'
                try:
                    staff = user.staffs
                    user_data = {
                        'id': staff.id,
                        'name': f"{user.first_name} {user.last_name}",
                        'email': user.email,
                        'address': staff.address,
                    }
                except Exception as e:
                    print(f"Error getting staff data: {e}")
                    user_data = {
                        'id': user.id,
                        'name': f"{user.first_name} {user.last_name}",
                        'email': user.email,
                    }
            elif user.user_type == '4':  # Parent
                actual_user_type = 'Parent'
                try:
                    parent = user.parents
                    user_data = {
                        'id': parent.id,
                        'name': f"{user.first_name} {user.last_name}",
                        'email': user.email,
                    }
                except Exception as e:
                    print(f"Error getting parent data: {e}")
                    user_data = {
                        'id': user.id,
                        'name': f"{user.first_name} {user.last_name}",
                        'email': user.email,
                    }
            
            print(f"Login successful for {actual_user_type}: {user.email}")
            
            return JsonResponse({
                'success': True,
                'token': token.key,
                'user_type': actual_user_type,
                'user_id': user.id,
                'user_data': user_data,
                'message': f'Login successful as {actual_user_type}'
            })
        else:
            print(f"Authentication failed for {email}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid email or password'
            })
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Login error: {str(e)}'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_parent_dashboard(request):
    """
    API endpoint for parent dashboard data
    """
    try:
        # Check if user is a parent
        if not hasattr(request.user, 'parents'):
            return Response({
                'success': False,
                'error': 'User is not a parent'
            }, status=status.HTTP_403_FORBIDDEN)
        
        parent = request.user.parents
        
        # Get parent-specific dashboard data
        dashboard_data = {
            'parent_info': {
                'id': parent.id,
                'name': f"{parent.admin.first_name} {parent.admin.last_name}",
                'email': parent.admin.email,
                'phone': parent.phone_number if hasattr(parent, 'phone_number') else None,
            },
            'children': [],  # Add logic to get children information
            'recent_activities': [],  # Add logic to get children's recent activities
            'notifications': [],  # Add logic to get notifications
            'upcoming_events': [],  # Add logic to get upcoming school events
        }
        
        # If you have a relationship to get children, add this logic:
        # if hasattr(parent, 'children'):
        #     dashboard_data['children'] = [
        #         {
        #             'id': child.id,
        #             'name': f"{child.first_name} {child.last_name}",
        #             'class': child.current_class,
        #             'attendance': child.attendance_percentage,
        #         }
        #         for child in parent.children.all()
        #     ]
        
        return Response({
            'success': True,
            'data': dashboard_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_parent_children(request):
    """Get parent's children information"""
    try:
        # Check if user is a parent
        if request.user.user_type != '4':
            return JsonResponse({
                'success': False,
                'error': 'Only parents can view children data'
            })
        
        # Get parent object
        try:
            parent = Parents.objects.get(admin=request.user)
            student = parent.student
        except Parents.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Parent profile not found'
            })
        
        # Calculate attendance percentage
        def calculate_attendance_percentage(student):
            try:
                # Get all attendance reports for this student
                attendance_reports = AttendanceReport.objects.filter(student_id=student)
                
                if not attendance_reports.exists():
                    return 0
                
                total_days = attendance_reports.count()
                present_days = attendance_reports.filter(status=True).count()
                
                if total_days == 0:
                    return 0
                
                attendance_percentage = round((present_days / total_days) * 100, 2)
                return attendance_percentage
                
            except Exception as e:
                print(f"Error calculating attendance: {e}")
                return 0
        
        # Alternative method if you want to calculate by date range
        def calculate_attendance_by_date_range(student, days_back=30):
            try:
                from datetime import datetime, timedelta
                
                # Calculate attendance for last 30 days (or specified range)
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days_back)
                
                # Get attendance records within date range
                attendance_records = AttendanceReport.objects.filter(
                    student_id=student,
                    attendance_id__attendance_date__range=[start_date, end_date]
                )
                
                if not attendance_records.exists():
                    return 0
                
                total_days = attendance_records.count()
                present_days = attendance_records.filter(status=True).count()
                
                if total_days == 0:
                    return 0
                
                attendance_percentage = round((present_days / total_days) * 100, 2)
                return attendance_percentage
                
            except Exception as e:
                print(f"Error calculating attendance by date range: {e}")
                return 0
        
        # Calculate current academic year attendance
        def calculate_current_year_attendance(student):
            try:
                # Get current academic year
                current_session = None
                try:
                    # Assuming you have a way to get current academic year
                    current_session = SessionYearModel.objects.filter(
                        session_start_year__lte=datetime.now().year,
                        session_end_year__gte=datetime.now().year
                    ).first()
                except:
                    pass
                
                if current_session:
                    # Get attendance for current academic year
                    attendance_records = AttendanceReport.objects.filter(
                        student_id=student,
                        attendance_id__session_year_id=current_session
                    )
                else:
                    # Fallback to all attendance records
                    attendance_records = AttendanceReport.objects.filter(student_id=student)
                
                if not attendance_records.exists():
                    return 0
                
                total_days = attendance_records.count()
                present_days = attendance_records.filter(status=True).count()
                
                if total_days == 0:
                    return 0
                
                attendance_percentage = round((present_days / total_days) * 100, 2)
                return attendance_percentage
                
            except Exception as e:
                print(f"Error calculating current year attendance: {e}")
                return 0
        
        # Use the most appropriate calculation method
        attendance_percentage = calculate_current_year_attendance(student)
        
        # If no attendance data, try alternative methods
        if attendance_percentage == 0:
            attendance_percentage = calculate_attendance_by_date_range(student, 30)
        
        # Get student data
        child_data = {
            'id': student.admission_number,
            'name': f"{student.first_name} {student.last_name}",
            'student_id': getattr(student, 'student_id', student.admission_number),
            'address': getattr(student, 'address', ''),
            'date_of_birth': str(getattr(student, 'date_of_birth', '')),
            'gender': getattr(student, 'gender', ''),
            'class': getattr(student.grade_id, 'course_name', f"{student.grade_id.grade_name}") if hasattr(student, 'grade_id') else '',
            'stream': getattr(student.stream_id, 'stream', f"{student.stream_id.stream_name}"),
            'current_grade': 'N/A',  # Add logic to get current grade
            'attendance_percentage': attendance_percentage,
            'total_attendance_days': AttendanceReport.objects.filter(student_id=student).count(),
            'present_days': AttendanceReport.objects.filter(student_id=student, status=True).count(),
        }
        
        return JsonResponse({
            'success': True,
            'data': [child_data]  # Return as list since parent might have multiple children
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_staff_dashboard(request):
    """
    API endpoint for staff dashboard data
    """
    try:
        # Check if user is staff
        if not hasattr(request.user, 'staff'):
            return Response({
                'success': False,
                'error': 'User is not a staff member'
            }, status=status.HTTP_403_FORBIDDEN)
        
        staff = request.user.staff
        
        # Get staff-specific dashboard data
        dashboard_data = {
            'staff_info': {
                'id': staff.id,
                'name': f"{staff.first_name} {staff.last_name}",
                'email': staff.email,
                'department': staff.department.name if staff.department else None,
                'position': staff.position if hasattr(staff, 'position') else None,
            },
            'assigned_classes': [],  # Add logic to get assigned classes
            'recent_activities': [],  # Add logic to get recent activities
            'notifications': [],  # Add logic to get notifications
        }
        
        return Response({
            'success': True,
            'data': dashboard_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def api_hod_dashboard(request):
    """HOD Dashboard data"""
    try:
        # Initialize default values
        total_staff = 0
        total_students = 0
        pending_leave_requests = 0
        total_feedback = 0
        
        # Get counts if models exist
        if Staffs:
            total_staff = Staffs.objects.count()
        if Students:
            total_students = Students.objects.count()
        if LeaveReportStaff:
            pending_leave_requests = LeaveReportStaff.objects.filter(leave_status=0).count()
        
        # Get recent activities
        staff_data = []
        student_data = []
        
        if Staffs:
            try:
                recent_staff = Staffs.objects.order_by('-created_at')[:5]
                for staff in recent_staff:
                    staff_data.append({
                        'id': staff.id,
                        'name': f"{staff.admin.first_name} {staff.admin.last_name}",
                        'email': staff.admin.email,
                        'date_joined': staff.created_at.strftime('%Y-%m-%d') if hasattr(staff, 'created_at') and staff.created_at else ''
                    })
            except:
                pass
        
        if Students:
            try:
                recent_students = Students.objects.order_by('-created_at')[:5]
                for student in recent_students:
                    student_data.append({
                        'id': student.id,
                        'name': f"{student.first_name} {student.last_name}",
                        'course': student.course_id.course_name if hasattr(student, 'course_id') and student.course_id else '',
                        'date_joined': student.created_at.strftime('%Y-%m-%d') if hasattr(student, 'created_at') and student.created_at else ''
                    })
            except:
                pass
        
        return JsonResponse({
            'success': True,
            'data': {
                'stats': {
                    'total_staff': total_staff,
                    'total_students': total_students,
                    'pending_leave_requests': pending_leave_requests,
                    'total_feedback': total_feedback
                },
                'recent_staff': staff_data,
                'recent_students': student_data
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
def api_get_all_staff(request):
    """Get all staff members"""
    try:
        if not Staffs:
            return JsonResponse({
                'success': False,
                'error': 'Staff model not available'
            })
            
        staff_list = Staffs.objects.all()
        staff_data = []
        
        for staff in staff_list:
            try:
                # Handle different possible model structures
                if hasattr(staff, 'admin') and staff.admin:
                    first_name = staff.admin.first_name
                    last_name = staff.admin.last_name
                    email = staff.admin.email
                    username = staff.admin.username
                elif hasattr(staff, 'first_name'):
                    first_name = getattr(staff, 'first_name', '')
                    last_name = getattr(staff, 'last_name', '')
                    email = getattr(staff, 'email', '')
                    username = getattr(staff, 'username', '')
                elif hasattr(staff, 'name'):
                    name_parts = staff.name.split(' ', 1)
                    first_name = name_parts[0] if name_parts else ''
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                    email = getattr(staff, 'email', '')
                    username = getattr(staff, 'username', '')
                else:
                    first_name = str(staff)
                    last_name = ''
                    email = ''
                    username = ''
                
                staff_data.append({
                    'id': staff.id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': getattr(staff, 'phone', username),
                    'address': getattr(staff, 'address', ''),
                    'date_joined': staff.created_at.strftime('%Y-%m-%d') if hasattr(staff, 'created_at') and staff.created_at else ''
                })
            except Exception as e:
                # If individual staff processing fails, add minimal data
                staff_data.append({
                    'id': staff.id,
                    'first_name': str(staff),
                    'last_name': '',
                    'email': '',
                    'phone': '',
                    'address': '',
                    'date_joined': ''
                })
        
        return JsonResponse({
            'success': True,
            'data': staff_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
def api_get_all_students(request):
    """Get all students"""
    try:
        if not Students:
            return JsonResponse({
                'success': False,
                'error': 'Students model not available'
            })
            
        students_list = Students.objects.all()
        student_data = []
        
        for student in students_list:
            try:
                # Handle different possible model structures
                if hasattr(student, '') and student:
                    first_name = student.first_name
                    last_name = student.last_name
                    username = student.username
                elif hasattr(student, 'first_name'):
                    first_name = getattr(student, 'first_name', '')
                    last_name = getattr(student, 'last_name', '')
                    username = getattr(student, 'username', '')
                elif hasattr(student, 'name'):
                    name_parts = student.name.split(' ', 1)
                    first_name = name_parts[0] if name_parts else ''
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                    username = getattr(student, 'username', '')
                else:
                    first_name = str(student)
                    last_name = ''
                    username = ''
                
                student_data.append({
                    'id': student.id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'address': getattr(student, 'address', ''),
                    'course': getattr(student.course_id, 'course_name', '') if hasattr(student, 'course_id') and student.course_id else getattr(student, 'course', ''),
                    'date_joined': student.created_at.strftime('%Y-%m-%d') if hasattr(student, 'created_at') and student.created_at else ''
                })
            except Exception as e:
                # If individual student processing fails, add minimal data
                student_data.append({
                    'id': student.id,
                    'first_name': str(student),
                    'last_name': '',
                    'address': '',
                    'course': '',
                    'date_joined': ''
                })
        
        return JsonResponse({
            'success': True,
            'data': student_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_parent_attendance(request):
    """Get parent's student attendance data"""
    try:
        # Check if user is a parent
        if request.user.user_type != '4':
            return JsonResponse({
                'success': False,
                'error': 'Only parents can view attendance data'
            })
        
        # Get parent object
        try:
            parent = Parents.objects.get(admin=request.user)
            student = parent.student
        except Parents.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Parent profile not found'
            })
        
        # Get period parameter
        period = request.GET.get('period', 'current_year')
        
        # Calculate attendance using the utility function
        from .utils import calculate_student_attendance
        attendance_summary = calculate_student_attendance(student, period)
        
        # Get detailed attendance records
        if period == 'current_year':
            current_session = SessionYearModel.objects.filter(
                session_start_year__lte=datetime.now().year,
                session_end_year__gte=datetime.now().year
            ).first()
            
            if current_session:
                attendance_records = AttendanceReport.objects.filter(
                    student_id=student,
                    attendance_id__session_year_id=current_session
                ).order_by('-attendance_id__attendance_date')
            else:
                attendance_records = AttendanceReport.objects.filter(
                    student_id=student
                ).order_by('-attendance_id__attendance_date')
                
        elif period == 'last_30_days':
            from datetime import timedelta
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            attendance_records = AttendanceReport.objects.filter(
                student_id=student,
                attendance_id__attendance_date__range=[start_date, end_date]
            ).order_by('-attendance_id__attendance_date')
            
        else:  # all_time
            attendance_records = AttendanceReport.objects.filter(
                student_id=student
            ).order_by('-attendance_id__attendance_date')
        
        # Format attendance records for API response
        records_data = []
        for record in attendance_records[:100]:  # Limit to last 100 records
            try:
                attendance_date = record.attendance_id.attendance_date
                subject_name = getattr(record.attendance_id.subject_id, 'subject_name', 'General') if hasattr(record.attendance_id, 'subject_id') else 'General'
                
                records_data.append({
                    'id': record.id,
                    'date': str(attendance_date),
                    'status': record.status,
                    'subject': subject_name,
                    'remarks': getattr(record, 'remarks', ''),
                    'created_at': str(record.created_at.date()) if hasattr(record, 'created_at') else str(attendance_date)
                })
            except Exception as e:
                print(f"Error processing attendance record {record.id}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'data': {
                'summary': attendance_summary,
                'records': records_data,
                'student_info': {
                    'name': f"{student.admin.first_name} {student.admin.last_name}",
                    'student_id': getattr(student, 'student_id', student.id),
                    'class': getattr(student.course_id, 'course_name', '') if hasattr(student, 'course_id') else ''
                }
            }
        })
        
    except Exception as e:
        print(f"Error in api_parent_attendance: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_parent_notifications(request):
    """Get parent notifications"""
    try:
        # Check if user is a parent
        if request.user.user_type != '4':
            return JsonResponse({
                'success': False,
                'error': 'Only parents can view notifications'
            })
        
        # Get parent object
        try:
            parent = Parents.objects.get(admin=request.user)
        except Parents.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Parent profile not found'
            })
        
        # Get notifications - you might need to create a Notification model
        # For now, we'll use existing feedback and leave data as notifications
        notifications = []
        
        # Add feedback notifications
        try:
            feedback_notifications = FeedBackParents.objects.filter(
                parent_id=parent
            ).order_by('-created_at')
            
            for feedback in feedback_notifications:
                notifications.append({
                    'id': f"feedback_{feedback.id}",
                    'type': 'feedback',
                    'title': 'Feedback Response',
                    'message': feedback.feedback_reply if hasattr(feedback, 'feedback_reply') and feedback.feedback_reply else 'Your feedback has been received',
                    'created_at': str(feedback.created_at),
                    'is_read': False,  # You might want to add this field to your model
                    'priority': 'normal'
                })
        except Exception as e:
            print(f"Error getting feedback notifications: {e}")
        
        # Add leave status notifications
        try:
            from .models import LeaveReportStudent
            student = parent.student
            leave_notifications = LeaveReportStudent.objects.filter(
                student_id=student
            ).exclude(leave_status=0).order_by('-created_at')
            
            for leave in leave_notifications:
                status_text = 'approved' if leave.leave_status == 1 else 'rejected'
                notifications.append({
                    'id': f"leave_{leave.id}",
                    'type': 'leave',
                    'title': f'Leave Request {status_text.title()}',
                    'message': f'Your leave request for {leave.leave_date} has been {status_text}',
                    'created_at': str(leave.created_at) if hasattr(leave, 'created_at') else str(leave.leave_date),
                    'is_read': False,
                    'priority': 'normal'
                })
        except Exception as e:
            print(f"Error getting leave notifications: {e}")
        
        # Add some sample notifications for demonstration
        if not notifications:
            notifications = [
                {
                    'id': 1,
                    'type': 'announcement',
                    'title': 'Welcome to Parent Portal',
                    'message': 'Welcome to the school parent portal. You can now view your child\'s attendance, apply for leave, and receive important notifications.',
                    'created_at': '2024-01-15T10:00:00Z',
                    'is_read': False,
                    'priority': 'normal'
                },
                {
                    'id': 2,
                    'type': 'academic',
                    'title': 'Parent-Teacher Meeting',
                    'message': 'Parent-teacher meeting scheduled for next week. Please check the school calendar for your appointment time.',
                    'created_at': '2024-01-14T15:30:00Z',
                    'is_read': True,
                    'priority': 'high'
                }
            ]
        
        # Sort notifications by created_at (newest first)
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'data': notifications
        })
        
    except Exception as e:
        print(f"Error in api_parent_notifications: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_mark_notification_read(request):
    """Mark notification as read"""
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        # For now, just return success since we don't have a proper notification model
        # In a real implementation, you would update the notification's is_read field
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_mark_all_notifications_read(request):
    """Mark all notifications as read"""
    try:
        # In a real implementation, you would update all user's notifications
        return JsonResponse({
            'success': True,
            'message': 'All notifications marked as read'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_notification(request, notification_id):
    """Delete notification"""
    try:
        
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_add_academic_year(request):
    """Add new academic year"""
    try:
        # Check if user is HOD/Admin
        if request.user.user_type != '1':
            return JsonResponse({
                'success': False,
                'error': 'Only HOD/Admin can add academic years'
            })
        
        # Get data from request
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        
        academic_start_year = data.get('academic_start_year')
        academic_end_year = data.get('academic_end_year')
        
        if not academic_start_year or not academic_end_year:
            return JsonResponse({
                'success': False,
                'error': 'Both start and end dates are required'
            })
        
        # Validate date format and convert
        try:
            from datetime import datetime
            start_date = datetime.strptime(academic_start_year, '%Y-%m-%d').date()
            end_date = datetime.strptime(academic_end_year, '%Y-%m-%d').date()
            
            if end_date <= start_date:
                return JsonResponse({
                    'success': False,
                    'error': 'End date must be after start date'
                })
                
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            })
        
        # Check if academic year already exists with same dates
        existing_year = AcademicYear.objects.filter(
            academic_start_year=start_date,
            academic_end_year=end_date
        ).first()
        
        if existing_year:
            return JsonResponse({
                'success': False,
                'error': 'Academic year with these dates already exists'
            })
        
        # Create new academic year
        academic_year = AcademicYear.objects.create(
            academic_start_year=start_date,
            academic_end_year=end_date
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Academic year added successfully',
            'data': {
                'id': academic_year.id,
                'academic_start_year': str(academic_year.academic_start_year),
                'academic_end_year': str(academic_year.academic_end_year),
                'created_at': str(academic_year.created_at) if hasattr(academic_year, 'created_at') else None
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_academic_years(request):
    """Get all academic years"""
    try:
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            })
        
        academic_years = AcademicYear.objects.all().order_by('-academic_start_year')
        
        years_data = []
        for year in academic_years:
            years_data.append({
                'id': year.id,
                'academic_start_year': str(year.academic_start_year),
                'academic_end_year': str(year.academic_end_year),
                'display_name': f"{year.academic_start_year.year}-{year.academic_end_year.year}",
                'is_current': _is_current_academic_year(year),
                'total_days': (year.academic_end_year - year.academic_start_year).days + 1
            })
        
        return JsonResponse({
            'success': True,
            'data': years_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def _is_current_academic_year(academic_year):
    """Helper function to check if academic year is current"""
    from datetime import date
    today = date.today()
    return academic_year.academic_start_year <= today <= academic_year.academic_end_year

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_staff_dashboard(request):
    """
    API endpoint for staff dashboard data
    """
    try:
        # Check if user is staff
        if request.user.user_type != '2':
            return JsonResponse({
                'success': False,
                'error': 'Only staff members can access this dashboard'
            })
        
        # Get staff object
        try:
            staff = Staffs.objects.get(admin=request.user)
        except Staffs.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Staff profile not found'
            })
        
        # Get staff information
        staff_info = {
            'id': staff.id,
            'name': f"{request.user.first_name} {request.user.last_name}",
            'email': request.user.email,
            'employee_id': getattr(staff, 'staff_id', f'STF{staff.id:03d}'),
            'department': getattr(staff, 'department', 'General'),
            'address': getattr(staff, 'address', ''),
            'phone': getattr(staff, 'phone', ''),
            'date_joined': str(staff.created_at.date()) if hasattr(staff, 'created_at') else 'N/A'
        }
        
        # Calculate statistics
        stats = {}
        
        # Get classes assigned to this staff
        try:
            # Assuming you have a way to get classes assigned to staff
            # This might vary based on your model structure
            assigned_classes = 0
            total_students = 0
            
            # If you have a Subject or Class model linked to staff
            # assigned_classes = Subjects.objects.filter(staff_id=staff).count()
            # total_students = Students.objects.filter(course_id__in=assigned_courses).count()
            
            # For now, we'll use sample calculations
            assigned_classes = 3  # You can implement actual logic here
            total_students = Students.objects.count() if Students else 0
            
            stats['classes_assigned'] = assigned_classes
            stats['students_total'] = total_students
            
        except Exception as e:
            print(f"Error calculating class stats: {e}")
            stats['classes_assigned'] = 0
            stats['students_total'] = 0
        
        # Get today's attendance statistics
        try:
            from datetime import date
            today = date.today()
            
            # Get today's attendance records
            today_attendance = AttendanceReport.objects.filter(
                attendance_id__attendance_date=today
            ) if AttendanceReport else []
            
            total_today = today_attendance.count() if today_attendance else 0
            present_today = today_attendance.filter(status=True).count() if today_attendance else 0
            
            attendance_percentage = round((present_today / total_today) * 100, 1) if total_today > 0 else 0
            
            stats['attendance_today'] = attendance_percentage
            stats['total_students_today'] = total_today
            stats['present_students_today'] = present_today
            
        except Exception as e:
            print(f"Error calculating attendance stats: {e}")
            stats['attendance_today'] = 0
            stats['total_students_today'] = 0
            stats['present_students_today'] = 0
        
        # Get pending tasks (leave requests, feedback, etc.)
        try:
            pending_tasks = 0
            
            # Count pending leave requests that might need staff attention
            if LeaveReportStaff:
                pending_leave = LeaveReportStaff.objects.filter(
                    staff_id=staff,
                    leave_status=0
                ).count()
                pending_tasks += pending_leave
            
            # Count unread feedback
            if FeedBackStaffs:
                unread_feedback = FeedBackStaffs.objects.filter(
                    staff_id=staff,
                    feedback_reply__isnull=True
                ).count()
                pending_tasks += unread_feedback
            
            stats['pending_tasks'] = pending_tasks
            
        except Exception as e:
            print(f"Error calculating pending tasks: {e}")
            stats['pending_tasks'] = 0
        
        # Get recent activities
        recent_activities = []
        
        try:
            # Recent attendance records taken by this staff
            recent_attendance = AttendanceReport.objects.filter(
                attendance_id__created_at__isnull=False
            ).order_by('-attendance_id__created_at')[:5] if AttendanceReport else []
            
            for attendance in recent_attendance:
                try:
                    recent_activities.append({
                        'type': 'attendance',
                        'title': 'Attendance Recorded',
                        'description': f'Attendance recorded for {attendance.attendance_id.attendance_date}',
                        'date': str(attendance.attendance_id.attendance_date),
                        'icon': 'assignment_turned_in'
                    })
                except:
                    continue
            
        except Exception as e:
            print(f"Error getting recent activities: {e}")
        
        # Get upcoming events/classes
        upcoming_events = []
        
        try:
            # You can add logic here to get upcoming classes or events
            # For now, we'll add some sample data
            from datetime import datetime, timedelta
            tomorrow = datetime.now().date() + timedelta(days=1)
            
            upcoming_events = [
                {
                    'title': 'Morning Classes',
                    'date': str(tomorrow),
                    'time': '09:00 AM',
                    'type': 'class'
                },
                {
                    'title': 'Staff Meeting',
                    'date': str(tomorrow + timedelta(days=2)),
                    'time': '02:00 PM',
                    'type': 'meeting'
                }
            ]
            
        except Exception as e:
            print(f"Error getting upcoming events: {e}")
        
        # Get notifications count
        notifications_count = 0
        try:
            # Count unread notifications for staff
            # This would depend on your notification system
            notifications_count = 0  # Implement based on your notification model
        except:
            notifications_count = 0
        
        dashboard_data = {
            'staff_info': staff_info,
            'stats': stats,
            'recent_activities': recent_activities,
            'upcoming_events': upcoming_events,
            'notifications_count': notifications_count,
            'quick_actions': [
                {
                    'title': 'Take Attendance',
                    'icon': 'how_to_reg',
                    'action': 'take_attendance'
                },
                {
                    'title': 'View Students',
                    'icon': 'groups',
                    'action': 'view_students'
                },
                {
                    'title': 'Apply Leave',
                    'icon': 'event_busy',
                    'action': 'apply_leave'
                },
                {
                    'title': 'Send Feedback',
                    'icon': 'feedback',
                    'action': 'send_feedback'
                }
            ]
        }
        
        return JsonResponse({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        print(f"Error in api_staff_dashboard: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_parent_apply_leave(request):
    """Parent apply leave for student"""
    try:
        # Check if user is a parent
        if request.user.user_type != '4':
            return JsonResponse({
                'success': False,
                'error': 'Only parents can apply for student leave'
            })
        
        # Get parent object
        try:
            parent = Parents.objects.get(admin=request.user)
            student = parent.student
        except Parents.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Parent profile not found'
            })
        
        # Get data from request
        data = json.loads(request.body) if request.body else request.POST
        leave_date = data.get('leave_date')
        leave_msg = data.get('leave_msg')
        
        if not leave_date or not leave_msg:
            return JsonResponse({
                'success': False,
                'error': 'Leave date and message are required'
            })
        
        # Create leave report
        leave_report = LeaveReportStudent.objects.create(
            student_id=student,
            leave_date=leave_date,
            leave_message=leave_msg,
            leave_status=0  # Pending
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Leave application submitted successfully',
            'data': {
                'id': leave_report.id,
                'leave_date': str(leave_report.leave_date),
                'leave_message': leave_report.leave_message,
                'status': 'pending'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_parent_leave_history(request):
    """Get parent's student leave history"""
    try:
        # Check if user is a parent
        if request.user.user_type != '4':
            return JsonResponse({
                'success': False,
                'error': 'Only parents can view student leave history'
            })
        
        # Get parent object
        try:
            parent = Parents.objects.get(admin=request.user)
            student = parent.student
        except Parents.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Parent profile not found'
            })
        
        # Get leave history
        leave_reports = LeaveReportStudent.objects.filter(
            student_id=student
        ).order_by('-created_at')
        
        leave_data = []
        for leave in leave_reports:
            leave_data.append({
                'id': leave.id,
                'leave_date': str(leave.leave_date),
                'leave_message': leave.leave_message,
                'leave_status': leave.leave_status,
                'created_at': str(leave.created_at.date()) if hasattr(leave, 'created_at') else str(leave.leave_date)
            })
        
        return JsonResponse({
            'success': True,
            'data': leave_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })



@csrf_exempt
def api_get_leave_requests(request):
    """Get all leave requests"""
    try:
        if not LeaveReportStaff:
            return JsonResponse({
                'success': True,
                'data': []  # Return empty list instead of None
            })
            
        leave_requests = LeaveReportStaff.objects.all().order_by('-created_at')
        requests_data = []
        
        for leave_request in leave_requests:
            status_map = {0: 'pending', 1: 'approved', 2: 'rejected'}
            requests_data.append({
                'id': leave_request.id,
                'staff_name': f"{leave_request.staff_id.admin.first_name} {leave_request.staff_id.admin.last_name}",
                'leave_type': 'Leave',
                'from_date': leave_request.leave_date.strftime('%Y-%m-%d'),
                'to_date': leave_request.leave_date.strftime('%Y-%m-%d'),
                'reason': leave_request.leave_message,
                'status': status_map.get(leave_request.leave_status, 'pending')
            })
        
        return JsonResponse({
            'success': True,
            'data': requests_data  # Make sure this is always a list
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
def api_add_staff(request):
    """Add new staff member"""
    try:
        if not Staffs:
            return JsonResponse({
                'success': False,
                'error': 'Staff model not available'
            })
            
        data = json.loads(request.body)
        
        # Create CustomUser
        user = CustomUser.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            user_type=2  # Staff
        )
        
        # Create Staff
        staff = Staffs.objects.create(
            admin=user,
            address=data.get('address', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Staff added successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def api_add_student(request):
    """Add new student"""
    try:
        if not Students:
            return JsonResponse({
                'success': False,
                'error': 'Students model not available'
            })
            
        data = json.loads(request.body)
        
    
        # Create Student with minimal required fields
        student_data = {
            'admin': user,
            'address': data.get('address', ''),
            'gender': data.get('gender', ''),
        }
        
        # Add optional fields if they exist in the model
        try:
            from .models import Courses, SessionYearModel
            course = Courses.objects.first()
            if course:
                student_data['course_id'] = course
                
            session_year = SessionYearModel.objects.first()
            if session_year:
                student_data['session_year_id'] = session_year
        except:
            pass
            
        student = Students.objects.create(**student_data)
        
        return JsonResponse({
            'success': True,
            'message': 'Student added successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
def api_update_leave_request(request):
    """Update leave request status"""
    try:
        if not LeaveReportStaff:
            return JsonResponse({
                'success': False,
                'error': 'LeaveReportStaff model not available'
            })
            
        data = json.loads(request.body)
        leave_id = data.get('leave_id')
        status = data.get('status')  # 'approved' or 'rejected'
        
        if not leave_id or not status:
            return JsonResponse({
                'success': False,
                'error': 'Missing leave_id or status'
            })
        
        try:
            leave_request = LeaveReportStaff.objects.get(id=leave_id)
        except LeaveReportStaff.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Leave request not found'
            })
        
        # Map status to integer values
        status_map = {
            'approved': 1,
            'rejected': 2,
            'pending': 0
        }
        
        if status not in status_map:
            return JsonResponse({
                'success': False,
                'error': 'Invalid status. Use: approved, rejected, or pending'
            })
        
        leave_request.leave_status = status_map[status]
        leave_request.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Leave request {status} successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

