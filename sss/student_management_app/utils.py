from datetime import datetime, timedelta
from .models import AttendanceReport, SessionYearModel

def calculate_student_attendance(student, method='current_year'):
    """
    Calculate student attendance percentage
    
    Args:
        student: Student object
        method: 'current_year', 'last_30_days', 'all_time'
    
    Returns:
        dict: {
            'percentage': float,
            'total_days': int,
            'present_days': int,
            'absent_days': int
        }
    """
    try:
        if method == 'current_year':
            # Get current academic year attendance
            try:
                current_session = SessionYearModel.objects.filter(
                    session_start_year__lte=datetime.now().year,
                    session_end_year__gte=datetime.now().year
                ).first()
                
                if current_session:
                    attendance_records = AttendanceReport.objects.filter(
                        student_id=student,
                        attendance_id__session_year_id=current_session
                    )
                else:
                    # Fallback to current year records
                    current_year = datetime.now().year
                    attendance_records = AttendanceReport.objects.filter(
                        student_id=student,
                        attendance_id__attendance_date__year=current_year
                    )
            except Exception as e:
                print(f"Error getting current year attendance: {e}")
                attendance_records = AttendanceReport.objects.filter(student_id=student)
                
        elif method == 'last_30_days':
            # Get attendance for last 30 days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            attendance_records = AttendanceReport.objects.filter(
                student_id=student,
                attendance_id__attendance_date__range=[start_date, end_date]
            )
            
        else:  # all_time
            attendance_records = AttendanceReport.objects.filter(student_id=student)
        
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status=True).count()
        absent_days = total_days - present_days
        
        if total_days == 0:
            percentage = 0.0
        else:
            percentage = round((present_days / total_days) * 100, 2)
        
        return {
            'percentage': percentage,
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days
        }
        
    except Exception as e:
        print(f"Error calculating attendance: {e}")
        return {
            'percentage': 0.0,
            'total_days': 0,
            'present_days': 0,
            'absent_days': 0
        }

def get_attendance_status_display(status):
    """Convert boolean status to display string"""
    if status is True:
        return 'Present'
    elif status is False:
        return 'Absent'
    else:
        return 'Unknown'

def calculate_monthly_attendance(student, year=None, month=None):
    """Calculate attendance for a specific month"""
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    try:
        attendance_records = AttendanceReport.objects.filter(
            student_id=student,
            attendance_id__attendance_date__year=year,
            attendance_id__attendance_date__month=month
        )
        
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status=True).count()
        
        if total_days == 0:
            return {'percentage': 0, 'total_days': 0, 'present_days': 0}
        
        percentage = round((present_days / total_days) * 100, 2)
        
        return {
            'percentage': percentage,
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': total_days - present_days
        }
        
    except Exception as e:
        print(f"Error calculating monthly attendance: {e}")
        return {'percentage': 0, 'total_days': 0, 'present_days': 0, 'absent_days': 0}
