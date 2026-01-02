from student_management_app.models import (
    LeaveReportStudent, LeaveReportStaff, 
    FeedBackParents, FeedBackStaffs,
    AttendanceChangeLog
)

def notifications_processor(request):
    """Context processor to provide notification data to all templates"""
    if not request.user.is_authenticated:
        return {}
        
    # Default empty data
    context_data = {
        'pending_leave_count': 0,
        'unread_feedback_count': 0,
        'recent_attendance_changes': [],
        'system_notifications': [],
        'recent_feedback_messages': []
    }
    
    # Only process for admin users (HOD)
    if hasattr(request.user, 'user_type') and request.user.user_type == '1':
        # Count pending leave requests
        pending_student_leaves = LeaveReportStudent.objects.filter(leave_status=0).count()
        pending_staff_leaves = LeaveReportStaff.objects.filter(leave_status=0).count()
        context_data['pending_leave_count'] = pending_student_leaves + pending_staff_leaves
        
        # Count unread feedback messages (those without replies)
        unread_parent_feedback = FeedBackParents.objects.filter(feedback_reply="").count()
        unread_staff_feedback = FeedBackStaffs.objects.filter(feedback_reply="").count()
        context_data['unread_feedback_count'] = unread_parent_feedback + unread_staff_feedback
        
        # Get recent attendance changes
        context_data['recent_attendance_changes'] = AttendanceChangeLog.objects.all().order_by('-change_date')[:5]
        
        # Get recent feedback messages
        parent_feedback = FeedBackParents.objects.all().order_by('-created_at')[:3]
        staff_feedback = FeedBackStaffs.objects.all().order_by('-created_at')[:3]
        
        # Combine and sort feedback messages
        all_feedback = []
        for feedback in parent_feedback:
            all_feedback.append({
                'id': feedback.id,
                'sender': f"{feedback.parent_id.admin.first_name} {feedback.parent_id.admin.last_name} (Parent)",
                'message': feedback.feedback,
                'date': feedback.created_at,
                'replied': bool(feedback.feedback_reply),
                'type': 'parent',
                'profile_pic': None  # Could add parent profile pic if available
            })
            
        for feedback in staff_feedback:
            all_feedback.append({
                'id': feedback.id,
                'sender': f"{feedback.staff_id.admin.first_name} {feedback.staff_id.admin.last_name} (Staff)",
                'message': feedback.feedback,
                'date': feedback.created_at,
                'replied': bool(feedback.feedback_reply),
                'type': 'staff',
                'profile_pic': None  # Could add staff profile pic if available
            })
            
        # Sort by date (newest first)
        all_feedback.sort(key=lambda x: x['date'], reverse=True)
        context_data['recent_feedback_messages'] = all_feedback[:5]
        
        # Get pending leave requests for notifications
        student_leaves = LeaveReportStudent.objects.filter(leave_status=0).order_by('-created_at')[:3]
        staff_leaves = LeaveReportStaff.objects.filter(leave_status=0).order_by('-created_at')[:3]
        
        leave_notifications = []
        for leave in student_leaves:
            leave_notifications.append({
                'id': leave.id,
                'name': f"{leave.student_id.first_name} {leave.student_id.last_name}",
                'type': 'Student Leave',
                'date': leave.created_at,
                'message': f"Requested leave for {leave.leave_date}",
                'url': 'student_leave_view'
            })
            
        for leave in staff_leaves:
            leave_notifications.append({
                'id': leave.id,
                'name': f"{leave.staff_id.admin.first_name} {leave.staff_id.admin.last_name}",
                'type': 'Staff Leave',
                'date': leave.created_at,
                'message': f"Requested leave for {leave.leave_date}",
                'url': 'staff_leave_view'
            })
            
        # Sort by date (newest first)
        leave_notifications.sort(key=lambda x: x['date'], reverse=True)
        
        # Add attendance changes as notifications
        attendance_notifications = []
        for change in context_data['recent_attendance_changes']:
            attendance_notifications.append({
                'id': change.id,
                'name': f"{change.changed_by.first_name} {change.changed_by.last_name}",
                'type': 'Attendance Change',
                'date': change.change_date,
                'message': f"Changed attendance for {change.attendance_report.student_id.first_name} {change.attendance_report.student_id.last_name}",
                'url': 'admin_view_attendance'
            })
            
        # Combine all notifications
        context_data['system_notifications'] = leave_notifications + attendance_notifications
        context_data['system_notifications'].sort(key=lambda x: x['date'], reverse=True)
        context_data['system_notifications'] = context_data['system_notifications'][:5]
        
    return context_data
