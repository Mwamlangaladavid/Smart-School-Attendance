from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from student_management_app.models import CustomUser, Parents, Students, Streams, AcademicYear, LeaveReportStudent, AttendanceReport, FeedBackParents

def parent_home(request):
    parent = Parents.objects.get(admin=request.user)
    student = parent.student
    
    total_streams = Streams.objects.filter(grade_id=student.grade_id).count()
    attendance_reports = AttendanceReport.objects.filter(student_id=student).order_by('-attendance_id__attendance_date')
    
    return render(request, "parent_template/parent_home_template.html", {
        "total_streams": total_streams,
        "attendance_reports": attendance_reports,
        "student": student
    })

def parent_apply_leave(request):
    parent = Parents.objects.get(admin=request.user)
    student = parent.student
    leave_data = LeaveReportStudent.objects.filter(student_id=student)
    return render(request, "parent_template/parent_apply_leave.html", {
        "leave_data": leave_data,
        "student": student
    })

def parent_apply_leave_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("parent_apply_leave"))
    
    parent = Parents.objects.get(admin=request.user)
    student = parent.student
    leave_date = request.POST.get("leave_date")
    leave_msg = request.POST.get("leave_msg")

    try:
        leave_report = LeaveReportStudent(
            student_id=student,
            leave_date=leave_date,
            leave_message=leave_msg,
            leave_status=0
        )
        leave_report.save()
        messages.success(request, "Successfully Applied for Leave")
        return HttpResponseRedirect(reverse("parent_apply_leave"))
    except:
        messages.error(request, "Failed To Apply for Leave")
        return HttpResponseRedirect(reverse("parent_apply_leave"))

def parent_feedback(request):
    parent_obj = Parents.objects.get(admin=request.user.id)
    feedback_data = FeedBackParents.objects.filter(parent_id=parent_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "parent_template/parent_feedback.html", context)

def parent_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('parent_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        parent_obj = Parents.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackParents(parent_id=parent_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('parent_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('parent_feedback')

def parent_view_attendance(request):
    """
    View function for parents to see attendance records for their children.
    Parents can view all attendance or filter by child, stream, and academic year.
    """
    # Get parent and their student
    parent = Parents.objects.get(admin=request.user.id)
    student = parent.student
    academic_years = AcademicYear.objects.all()
    
    if request.method == 'GET':
        context = {
            'student': student,
            'academic_years': academic_years
        }
        return render(request, 'parent_template/parent_view_attendance.htm', context)
        
    elif request.method == 'POST':
        # Get filter parameters
        academic_year_id = request.POST.get('academic_year')
        
        # Validate input
        if not academic_year_id:
            messages.error(request, "Please select an academic year")
            return redirect('parent_view_attendance')
            
        try:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        except AcademicYear.DoesNotExist:
            messages.error(request, "Invalid selection")
            return redirect('parent_view_attendance')
        
        # Get streams for this student's grade
        streams = Streams.objects.filter(grade_id=student.grade_id)
        
        # Get attendance reports for this student
        attendance_reports = AttendanceReport.objects.filter(
            student_id=student,
            attendance_id__academic_year_id=academic_year
        ).select_related('attendance_id', 'attendance_id__stream_id')
        
        # Calculate statistics including leave
        total_days = attendance_reports.count()
        present_count = attendance_reports.filter(status='1').count()
        absent_count = attendance_reports.filter(status='0').count()
        leave_count = attendance_reports.filter(status='L').count()
        
        # Calculate percentages
        if total_days > 0:
            present_percentage = round((present_count / total_days) * 100, 1)
            absent_percentage = round((absent_count / total_days) * 100, 1)
            leave_percentage = round((leave_count / total_days) * 100, 1)
        else:
            present_percentage = absent_percentage = leave_percentage = 0
        
        context = {
            'student': student,
            'academic_years': academic_years,
            'selected_academic_year': academic_year,
            'attendance_reports': attendance_reports,
            'total_days': total_days,
            'present_count': present_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'present_percentage': present_percentage,
            'absent_percentage': absent_percentage,
            'leave_percentage': leave_percentage,
        }
        
        return render(request, 'parent_template/parent_view_attendance.htm', context)

@csrf_exempt
def parent_get_attendance(request):
    stream_id=request.POST.get("stream")
    start_date=request.POST.get("start_date")
    end_date=request.POST.get("end_date")
    
    stream_obj=Streams.objects.get(id=stream_id)
    student_obj=Students.objects.get(id=request.user.id)
    attendance=Attendance.objects.filter(attendance_date__range=(start_date,end_date),stream_id=stream_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=student_obj)
    
    json_data=[]
    for attendance_report in attendance_reports:
        data={"id":attendance_report.id,"attendance_date":str(attendance_report.attendance_id.attendance_date),"status":attendance_report.status}
        json_data.append(data)
    return JsonResponse(json.dumps(json_data),safe=False)

def parent_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)

    context={
        "user":user,
        "parent":parent
    }
    return render(request,"parent_template/parent_profile.html", context)

def parent_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("parent_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("parent_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("parent_profile"))

@csrf_exempt
def parent_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        student=Students.objects.get(id=request.user.id)
        student.fcm_token=token
        student.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def parent_all_notifications(request):
    # Get the parent object for the current user
    parent = Parents.objects.get(admin=request.user)
    
    # Get the student associated with this parent
    student = parent.student
    
    # Get all notifications for this student
    notifications = NotificationStudent.objects.filter(student_id=student).order_by('-created_at')
    
    context = {
        "notifications": notifications
    }
    return render(request, "parent_template/all_notifications.html", context)
