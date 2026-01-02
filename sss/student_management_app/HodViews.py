from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from student_management_app.models import CustomUser, Staffs, Grades, Streams, Students, Parents,AttendanceChangeLog, AcademicYear, FeedBackParents, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport
from .forms import AddStudentForm, EditStudentForm
import datetime
import face_recognition
import numpy as np
from .models import FaceEncoding
import os
import csv
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import datetime, timedelta
import base64
from django.conf import settings
from .services import nextsms_service
import logging



def admin_home(request):
    all_student_count = Students.objects.all().count()
    stream_count = Streams.objects.all().count()
    grade_count = Grades.objects.all().count()
    staff_count = Staffs.objects.all().count()
    

    # Total streams and students in Each grade
    grade_all = Grades.objects.all()
    grade_name_list = []
    stream_count_list = []
    student_count_list_in_grade = []

    for grade in grade_all:
        streams = Streams.objects.filter(grade_id=grade.id).count()
        students = Students.objects.filter(grade_id=grade.id).count()
        grade_name_list.append(grade.grade_name)
        stream_count_list.append(streams)
        student_count_list_in_grade.append(students)
    
    stream_all = Streams.objects.all()
    stream_list = []
    student_count_list_in_stream = []
    for stream in stream_all:
        grade = Grades.objects.get(id=stream.grade_id.id)
        student_count = Students.objects.filter(grade_id=grade.id).count()
        stream_list.append(stream.stream_name)
        student_count_list_in_stream.append(student_count)
    
    # For Staffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        stream_ids = Streams.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(stream_id__in=stream_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status='1').count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status='0').count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(student.first_name)


    context={
        "all_student_count": all_student_count,
        "stream_count": stream_count,
        "grade_count": grade_count,
        "staff_count": staff_count,
        "grade_name_list": grade_name_list,
        "stream_count_list": stream_count_list,
        "student_count_list_in_grade": student_count_list_in_grade,
        "stream_list": stream_list,
        "student_count_list_in_stream": student_count_list_in_stream,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


import datetime

def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        # Auto-generate password if not provided
        if not password or password.strip() == "":
            current_year = datetime.datetime.now().year
            password = f"{last_name.lower()}@{current_year}"

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, f"Staff Added Successfully! Auto-generated password: {password}")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')



def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')




def add_grade(request):
    return render(request, "hod_template/add_grade_template.html")


def add_grade_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_grade')
    else:
        grade = request.POST.get('grade')
        try:
            grade_model = Grades(grade_name=grade)
            grade_model.save()
            messages.success(request, "grade Added Successfully!")
            return redirect('add_grade')
        except:
            messages.error(request, "Failed to Add grade!")
            return redirect('add_grade')


def manage_grade(request):
    grades = Grades.objects.all()
    context = {
        "grades": grades
    }
    return render(request, "hod_template/manage_grade_template.html", context)



def edit_grade(request, grade_id):
    grade = Grades.objects.get(id=grade_id)
    context = {
        "grade": grade,
        "id": grade_id
    }
    return render(request, 'hod_template/edit_grade_template.html', context)


def edit_grade_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        grade_id = request.POST.get('grade_id')
        grade_name = request.POST.get('grade')

        try:
            grade = Grades.objects.get(id=grade_id)
            grade.grade_name = grade_name
            grade.save()

            messages.success(request, "grade Updated Successfully.")
            return redirect('/edit_grade/'+grade_id)

        except:
            messages.error(request, "Failed to Update grade.")
            return redirect('/edit_grade/'+grade_id)


def delete_grade(request, grade_id):
    grade = Grades.objects.get(id=grade_id)
    try:
        grade.delete()
        messages.success(request, "grade Deleted Successfully.")
        return redirect('manage_grade')
    except:
        messages.error(request, "Failed to Delete grade.")
        return redirect('manage_grade')


def manage_academic_year(request):
    academic_years = AcademicYear.objects.all()
    context = {
        "academic_years": academic_years
    }
    return render(request, "hod_template/manage_academic_year_template.html", context)


def add_academic_year(request):
    return render(request, "hod_template/add_academic_year_template.html")


def add_academic_year_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_grade')
    else:
        academic_start_year = request.POST.get('academic_start_year')
        academic_end_year = request.POST.get('academic_end_year')

        try:
            academicyear = AcademicYear(academic_start_year=academic_start_year, academic_end_year=academic_end_year)
            academicyear.save()
            messages.success(request, "Academic Year added Successfully!")
            return redirect("add_academic_year")
        except:
            messages.error(request, "Failed to Add Academic Year")
            return redirect("add_academic_year")


def edit_academic_year(request, academic_id):
    academic_year = AcademicYear.objects.get(id=academic_id)
    context = {
        "academic_year": academic_year
    }
    return render(request, "hod_template/edit_academic_year_template.html", context)


def edit_academic_year_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_academic_year')
    else:
        academic_id = request.POST.get('academic_id')
        academic_start_year = request.POST.get('academic_start_year')
        academic_end_year = request.POST.get('academic_end_year')

        try:
            academic_year = AcademicYear.objects.get(id=academic_id)
            academic_year.academic_start_year = academic_start_year
            academic_year.academic_end_year = academic_end_year
            academic_year.save()

            messages.success(request, "Academic Year Updated Successfully.")
            return redirect('/edit_academic_year/'+academic_id)
        except:
            messages.error(request, "Failed to Update Academic Year.")
            return redirect('/edit_academic_year/'+academic_id)


def delete_academic_year(request, academic_id):
    academic = AcademicYear.objects.get(id=academic_id)
    try:
        academic.delete()
        messages.success(request, "Academic Deleted Successfully.")
        return redirect('manage_academic_year')
    except:
        messages.error(request, "Failed to Delete Academic.")
        return redirect('manage_academic_year')


def add_student(request):
    grades = Grades.objects.all()
    streams = Streams.objects.all()
    academic_years = AcademicYear.objects.all().order_by('academic_start_year')
 # Get all academic years ordered by name
    
    context = {
        "grades": grades,
        "streams": streams,
        "academic_years": academic_years
    }
    return render(request, 'hod_template/add_student_template.html', context)




def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        address = request.POST.get('address')
        nationality = request.POST.get('nationality')
        religion = request.POST.get('religion')
        disability = request.POST.get('disability')
        grade_id = request.POST.get('grade_id')
        stream_id = request.POST.get('stream_id')
        academic_year_id = request.POST.get('academic_year_id')

        # Check if profile picture was uploaded
        profile_pic = None
        if request.FILES.get('profile_pic', False):
            profile_pic = request.FILES['profile_pic']

        try:
            grade = Grades.objects.get(id=grade_id)
            stream = Streams.objects.get(id=stream_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
            
            student = Students(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=date_of_birth,
                address=address,
                nationality=nationality,
                religion=religion,
                disability=disability,
                grade_id=grade,
                stream_id=stream,
                academic_year_id=academic_year
            )
            
            # Add profile picture if uploaded
            if profile_pic:
                student.profile_pic = profile_pic
                
            student.save()
            
            # Generate face encoding if profile picture was uploaded
            if profile_pic:
                try:
                    # Get the path to the saved profile picture
                    image_path = student.profile_pic.path
                    
                    # Load the image and detect faces
                    image = face_recognition.load_image_file(image_path)
                    face_locations = face_recognition.face_locations(image)
                    
                    if face_locations:
                        # Get face encoding
                        face_encoding = face_recognition.face_encodings(image, face_locations)[0]
                        
                        # Save face encoding
                        FaceEncoding.objects.create(
                            student=student,
                            face_encoding=face_encoding.tobytes()
                        )
                        messages.success(request, "Student Added Successfully with Face Encoding!")
                    else:
                        messages.warning(request, "Student Added Successfully but no face detected in the profile picture. Please upload a clearer picture.")
                except Exception as e:
                    messages.warning(request, f"Student Added Successfully but face encoding failed: {str(e)}")
            else:
                messages.success(request, "Student Added Successfully! No profile picture provided.")
                
            return redirect('add_student')
        except Exception as e:
            messages.error(request, f"Failed to Add Student: {str(e)}")
            return redirect('add_student')




def manage_student(request):
    # Get filter parameters
    gender_filter = request.GET.get('gender', '')
    grade_filter = request.GET.get('grade', '')
    stream_filter = request.GET.get('stream', '')
    
    # Start with all students with related stream and staff
    students_query = Students.objects.select_related('stream_id__staff_id').all()
    
    # Apply filters if provided
    if gender_filter:
        students_query = students_query.filter(gender=gender_filter)
    
    if grade_filter:
        students_query = students_query.filter(grade_id=grade_filter)
        
    if stream_filter:
        students_query = students_query.filter(stream_id=stream_filter)
    
    students = students_query
    
    # Get all grades and streams for filter dropdowns
    grades = Grades.objects.all()
    streams = Streams.objects.all()
    
    # Check which students have face encodings
    for student in students:
        student.has_face_encoding = FaceEncoding.objects.filter(student=student).exists()
        
        # Get attendance statistics
        student.present_count = AttendanceReport.objects.filter(
            student_id=student,
            status='1'
        ).count()
        
        student.absent_count = AttendanceReport.objects.filter(
            student_id=student,
            status='0'
        ).count()
    
    # Get gender statistics
    total_students = students.count()
    male_count = students.filter(gender='M').count()
    female_count = students.filter(gender='F').count()
    
    context = {
        "students": students,
        "grades": grades,
        "streams": streams,
        "gender_filter": gender_filter,
        "grade_filter": grade_filter,
        "stream_filter": stream_filter,
        "total_students": total_students,
        "male_count": male_count,
        "female_count": female_count,
        "male_percentage": (male_count / total_students * 100) if total_students > 0 else 0,
        "female_percentage": (female_count / total_students * 100) if total_students > 0 else 0
    }
    return render(request, "hod_template/manage_student_template.html", context)



def edit_student(request, student_id):
    student = Students.objects.get(id=student_id)
    academic_years = AcademicYear.objects.all()
    grades = Grades.objects.all()
    streams = Streams.objects.all()

    form = EditStudentForm(initial={
        'student_id': student.id,
        'first_name': student.first_name,
        'middle_name': student.middle_name,
        'last_name': student.last_name,
        'gender': student.gender,
        'date_of_birth': student.date_of_birth,
        'residential_address': student.address,
        'nationality': student.nationality,
        'religion': student.religion,
        'disability': student.disability,
        'grade_id': student.grade_id,
        'stream_id': student.stream_id,
        'academic_year_id': student.academic_year_id
    })

    context = {
        'form': form,
        'student': student,
        'academic_years': academic_years,
        'grades': grades,
        'streams': streams
    }

    return render(request, 'hod_template/edit_student_template.html', context)

def edit_student_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("manage_student"))
        
    student_id = request.POST.get("student_id")
    first_name = request.POST.get("first_name")
    middle_name = request.POST.get("middle_name")
    last_name = request.POST.get("last_name")
    gender = request.POST.get("gender")
    date_of_birth = request.POST.get("date_of_birth")
    residential_address = request.POST.get("residential_address")
    nationality = request.POST.get("nationality")
    religion = request.POST.get("religion")
    disability = request.POST.get("disability")
    grade_id = request.POST.get("grade_id")
    stream_id = request.POST.get("stream_id")
    academic_year_id = request.POST.get("academic_year_id")

    # Check if new profile picture was uploaded
    new_profile_pic = None
    if request.FILES.get('student_image', False):
        new_profile_pic = request.FILES['student_image']

    try:
        student = Students.objects.get(id=student_id)
        student.first_name = first_name
        student.middle_name = middle_name
        student.last_name = last_name
        student.gender = gender
        student.date_of_birth = date_of_birth
        student.address = residential_address
        student.nationality = nationality
        student.religion = religion
        student.disability = disability
        student.grade_id = Grades.objects.get(id=grade_id)
        student.stream_id = Streams.objects.get(id=stream_id)
        student.academic_year_id = AcademicYear.objects.get(id=academic_year_id)

        # Update profile picture if a new one was uploaded
        if new_profile_pic:
            # Delete old picture if it exists
            if student.profile_pic:
                if os.path.exists(student.profile_pic.path):
                    os.remove(student.profile_pic.path)
            
            student.profile_pic = new_profile_pic
            
        student.save()
        
        # Update face encoding if a new profile picture was uploaded
        if new_profile_pic:
            try:
                # Get the path to the saved profile picture
                image_path = student.profile_pic.path
                
                # Load the image and detect faces
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image)
                
                if face_locations:
                    # Get face encoding
                    face_encoding = face_recognition.face_encodings(image, face_locations)[0]
                    
                    # Delete existing encoding if it exists
                    FaceEncoding.objects.filter(student=student).delete()
                    
                    # Save new face encoding
                    FaceEncoding.objects.create(
                        student=student,
                        face_encoding=face_encoding.tobytes()
                    )
                    messages.success(request, "Student updated successfully with new face encoding!")
                else:
                    messages.warning(request, "Student updated successfully but no face detected in the new profile picture. Please upload a clearer picture.")
            except Exception as e:
                messages.warning(request, f"Student updated successfully but face encoding failed: {str(e)}")
        else:
            messages.success(request, "Student updated successfully!")
            
        return HttpResponseRedirect(reverse("manage_student"))

    except Exception as e:
        messages.error(request, f"Failed to update student: {str(e)}")
        return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id":student_id}))

def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')

def add_parent(request):
    students = Students.objects.all()
    return render(request, "hod_template/add_parent_template.html", {"students": students})


def add_parent_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_parent')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        student_id = request.POST.get('student')
        
        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists. Please choose a different username.")
            return redirect('add_parent')
            
        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' already exists. Please use a different email.")
            return redirect('add_parent')

        # Auto-generate password if not provided
        if not password or password.strip() == "":
            current_year = datetime.datetime.now().year
            password = f"{last_name.lower()}@{current_year}"
            
        try:
            # Get the student by ID
            student = Students.objects.get(id=student_id)
            
            # Create the CustomUser first
            user = CustomUser.objects.create_user(
                username=username, 
                password=password, 
                first_name=first_name,
                last_name=last_name, 
                email=email, 
                user_type=4
            )
            
            # Create the Parents object directly with all required fields
            parent = Parents.objects.create(
                admin=user,
                student=student,
                address=address,
                phone_number=phone_number
            )
            
            # Send SMS notification to parent
            try:
                sms_message = (
                    f"Habari !, Ndugu {first_name} {last_name}, "
                    f"akaunti yako imetengenezwa kikamilifu. "
                    f"Taarifa za kuingilia kwenye akaunti yako ni  Username: {username}, Email: {email}, "
                    f"Password(Nywila): {password}. "
                    f"Tafadhari tunza taarifa hizi salama."
                )
                
                # Send SMS using NextSMS service
                sms_result = nextsms_service.send_single_sms(phone_number, sms_message)
                
                if sms_result['success']:
                    messages.success(
                        request, 
                        f"Parent Added Successfully! SMS notification sent to {phone_number}. "
                        f"Reference: {sms_result['reference']}. Auto-generated password: {password}"
                    )
                else:
                    messages.warning(
                        request, 
                        f"Parent Added Successfully! However, SMS notification failed: {sms_result.get('error', 'Unknown error')}. "
                        f"Auto-generated password: {password}"
                    )
                    
            except Exception as sms_error:
                # If SMS fails, still show success for parent creation
                messages.warning(
                    request, 
                    f"Parent Added Successfully! However, SMS notification failed: {str(sms_error)}. "
                    f"Auto-generated password: {password}"
                )
            
            return redirect('add_parent')
            
        except Students.DoesNotExist:
            messages.error(request, "Selected student does not exist")
            return redirect('add_parent')
        except Exception as e:
            messages.error(request, f"Failed to Add Parent: {e}")
            return redirect('add_parent')



def manage_parent(request):
    parents = Parents.objects.all()
    return render(request, "hod_template/manage_parent_template.html", {"parents": parents})

def edit_parent(request, parent_id):
    try:
        # Try to get the parent by ID
        parent = Parents.objects.get(id=parent_id)
        students = Students.objects.all()
        return render(request, "hod_template/edit_parent_template.html", {"parent": parent, "students": students})
    except Parents.DoesNotExist:
        # If that fails, log the error and redirect
        messages.error(request, f"Parent with ID {parent_id} not found")
        return redirect('manage_parent')


def edit_parent_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        parent_id = request.POST.get('parent_id')
        student_id = request.POST.get('student')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')

        try:
            # Get the parent by ID
            parent = Parents.objects.get(id=parent_id)
            
            # Update the CustomUser associated with this parent
            user = parent.admin
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            # Update the student relationship and phone number
            student = Students.objects.get(id=student_id)
            parent.student = student
            parent.phone_number = phone_number
            parent.save()

            messages.success(request, "Successfully Edited Parent")
            return redirect('/edit_parent/'+str(parent_id))
        except:
            messages.error(request, "Failed to Edit Parent")
            return redirect('/edit_parent/'+str(parent_id))

def delete_parent(request, parent_id):
    parent = Parents.objects.get(id=parent_id)
    try:
        user = parent.admin
        parent.delete()
        user.delete()
        messages.success(request, "Parent Deleted Successfully.")
        return redirect('manage_parent')
    except:
        messages.error(request, "Failed to Delete Parent.")
        return redirect('manage_parent')



def add_stream(request):
    grades = Grades.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)  # Filter for staff users
    
    context = {
        "grades": grades,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_stream_template.html', context)




def add_stream_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_stream')
    else:
        stream_name = request.POST.get('stream')

        grade_id = request.POST.get('grade')
        grade = Grades.objects.get(id=grade_id)
        
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            stream = Streams(stream_name=stream_name, grade_id=grade, staff_id=staff)
            stream.save()
            messages.success(request, "Stream Added Successfully!")
            return redirect('add_stream')
        except:
            messages.error(request, "Failed to Add Stream!")
            return redirect('add_stream')




def manage_stream(request):
    streams = Streams.objects.all()
    context = {
        "streams": streams
    }
    return render(request, 'hod_template/manage_stream_template.html', context)


def edit_stream(request, stream_id):
    stream = Streams.objects.get(id=stream_id)
    grades = Grades.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "stream": stream,
        "Grades": Grades,
        "staffs": staffs,
        "id": stream_id
    }
    return render(request, 'hod_template/edit_stream_template.html', context)


def edit_stream_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        stream_id = request.POST.get('stream_id')
        stream_name = request.POST.get('stream')
        grade_id = request.POST.get('grade')
        staff_id = request.POST.get('staff')

        try:
            stream = Streams.objects.get(id=stream_id)
            stream.stream_name = stream_name

            grade = Grades.objects.get(id=grade_id)
            stream.grade_id = grade

            staff = CustomUser.objects.get(id=staff_id)
            stream.staff_id = staff
            
            stream.save()

            messages.success(request, "stream Updated Successfully.")
            # return redirect('/edit_stream/'+stream_id)
            return HttpResponseRedirect(reverse("edit_stream", kwargs={"stream_id":stream_id}))

        except:
            messages.error(request, "Failed to Update stream.")
            return HttpResponseRedirect(reverse("edit_stream", kwargs={"stream_id":stream_id}))
            # return redirect('/edit_stream/'+stream_id)



def delete_stream(request, stream_id):
    stream = Streams.objects.get(id=stream_id)
    try:
        stream.delete()
        messages.success(request, "stream Deleted Successfully.")
        return redirect('manage_stream')
    except:
        messages.error(request, "Failed to Delete stream.")
        return redirect('manage_stream')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def parent_feedback_message(request):
    feedbacks = FeedBackParents.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/parent_feedback_template.html', context)


@csrf_exempt
def parent_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackParents.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    
    # Create or update attendance record for this student on the leave date
    student = leave.student_id
    leave_date = leave.leave_date
    
    # Find the student's stream
    stream = Streams.objects.filter(grade_id=student.grade_id).first()
    if stream:
        # Check if attendance record exists for this date and stream
        attendance = Attendance.objects.filter(
            attendance_date=leave_date,
            stream_id=stream,
            academic_year_id=student.academic_year_id
        ).first()
        
        if not attendance:
            # Create new attendance record
            attendance = Attendance.objects.create(
                attendance_date=leave_date,
                stream_id=stream,
                academic_year_id=student.academic_year_id
            )
        
        # Check if attendance report exists for this student
        attendance_report = AttendanceReport.objects.filter(
            student_id=student,
            attendance_id=attendance
        ).first()
        
        if attendance_report:
            # Update existing report to mark as leave
            attendance_report.status = 'L'
            attendance_report.save()
        else:
            # Create new attendance report with leave status
            AttendanceReport.objects.create(
                student_id=student,
                attendance_id=attendance,
                status='L'
            )
    
    # Send SMS notification to parent about leave approval
    try:
        # Get parent information
        parent = Parents.objects.filter(student=student).first()
        if parent and parent.phone_number:
            # Clean phone number - ensure it starts with 255
            clean_phone = parent.phone_number
            if not clean_phone.startswith('255'):
                clean_phone = '255' + clean_phone.lstrip('0+')
            
            # Format date - handle both string and date objects
            if hasattr(leave_date, 'strftime'):
                formatted_date = leave_date.strftime('%d/%m/%Y')
            else:
                # If it's already a string, try to parse it first
                from datetime import datetime
                try:
                    if isinstance(leave_date, str):
                        # Try different date formats
                        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                            try:
                                date_obj = datetime.strptime(leave_date, fmt)
                                formatted_date = date_obj.strftime('%d/%m/%Y')
                                break
                            except ValueError:
                                continue
                        else:
                            # If no format works, use the string as is
                            formatted_date = str(leave_date)
                    else:
                        formatted_date = str(leave_date)
                except Exception:
                    formatted_date = str(leave_date)
            
            sms_message = (
                f"Habari ,ndugu   {parent.admin.first_name} {parent.admin.last_name}, "
                f"Mzazi wa {student.first_name} {student.last_name} "
                f"ruhusa ya tarehe {formatted_date} IMEKUBALIWA ."
                
            )
            
            # Send SMS using NextSMS service
            from .services import nextsms_service
            
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Attempting to send SMS to: {clean_phone}")
            logger.info(f"SMS Message: {sms_message}")
            logger.info(f"Leave date type: {type(leave_date)}, value: {leave_date}")
            
            sms_result = nextsms_service.send_single_sms(clean_phone, sms_message)
            
            if sms_result['success']:
                messages.success(request, f"Leave approved and SMS notification sent to parent ({clean_phone}). Reference: {sms_result['reference']}")
                logger.info(f"SMS sent successfully. Reference: {sms_result['reference']}")
            else:
                messages.warning(request, f"Leave approved but SMS notification failed: {sms_result.get('error', 'Unknown error')}")
                logger.error(f"SMS failed: {sms_result.get('error')}")
        else:
            messages.success(request, "Leave approved but no parent contact found for SMS notification")
            
    except Exception as sms_error:
        messages.warning(request, f"Leave approved but SMS notification failed: {str(sms_error)}")
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"SMS exception: {str(sms_error)}")
    
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    
    # Create or update attendance record for this student on the leave date
    student = leave.student_id
    leave_date = leave.leave_date
    
    # Find the student's stream
    stream = Streams.objects.filter(grade_id=student.grade_id).first()
    if stream:
        # Check if attendance record exists for this date and stream
        attendance = Attendance.objects.filter(
            attendance_date=leave_date,
            stream_id=stream,
            academic_year_id=student.academic_year_id
        ).first()
        
        if not attendance:
            # Create new attendance record
            attendance = Attendance.objects.create(
                attendance_date=leave_date,
                stream_id=stream,
                academic_year_id=student.academic_year_id
            )
        
        # Check if attendance report exists for this student
        attendance_report = AttendanceReport.objects.filter(
            student_id=student,
            attendance_id=attendance
        ).first()
        
        if attendance_report:
            # Update existing report to mark as absent
            attendance_report.status = '0'
            attendance_report.save()
        else:
            # Create new attendance report with absent status
            AttendanceReport.objects.create(
                student_id=student,
                attendance_id=attendance,
                status='0'
            )
    
    # Send SMS notification to parent about leave rejection
    try:
        # Get parent information
        parent = Parents.objects.filter(student=student).first()
        if parent and parent.phone_number:
            # Clean phone number - ensure it starts with 255
            clean_phone = parent.phone_number
            if not clean_phone.startswith('255'):
                clean_phone = '255' + clean_phone.lstrip('0+')
            
            # Format date - handle both string and date objects
            if hasattr(leave_date, 'strftime'):
                formatted_date = leave_date.strftime('%d/%m/%Y')
            else:
                # If it's already a string, try to parse it first
                from datetime import datetime
                try:
                    if isinstance(leave_date, str):
                        # Try different date formats
                        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                            try:
                                date_obj = datetime.strptime(leave_date, fmt)
                                formatted_date = date_obj.strftime('%d/%m/%Y')
                                break
                            except ValueError:
                                continue
                        else:
                            # If no format works, use the string as is
                            formatted_date = str(leave_date)
                    else:
                        formatted_date = str(leave_date)
                except Exception:
                    formatted_date = str(leave_date)
            
            sms_message = (
                f"Habari, ndugu   {parent.admin.first_name} {parent.admin.last_name}, "
                f"mzazi wa {student.first_name} {student.last_name} "
                f"ruhusa ya tarehe {formatted_date} IMEKATALIWA. "
                f"Kwa maelezo zaidi walisiana na  Uongozi wa shule au mwalimu wa darasa. "
                
            )
            
            # Send SMS using NextSMS service
            from .services import nextsms_service
            
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Attempting to send SMS to: {clean_phone}")
            logger.info(f"SMS Message: {sms_message}")
            logger.info(f"Leave date type: {type(leave_date)}, value: {leave_date}")
            
            sms_result = nextsms_service.send_single_sms(clean_phone, sms_message)
            
            if sms_result['success']:
                messages.success(request, f"Leave rejected and SMS notification sent to parent ({clean_phone}). Reference: {sms_result['reference']}")
                logger.info(f"SMS sent successfully. Reference: {sms_result['reference']}")
            else:
                messages.warning(request, f"Leave rejected but SMS notification failed: {sms_result.get('error', 'Unknown error')}")
                logger.error(f"SMS failed: {sms_result.get('error')}")
        else:
            messages.success(request, "Leave rejected but no parent contact found for SMS notification")
            
    except Exception as sms_error:
        messages.warning(request, f"Leave rejected but SMS notification failed: {str(sms_error)}")
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"SMS exception: {str(sms_error)}")
    
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    
    grades = Grades.objects.all()
    academic_years = AcademicYear.objects.all()
    
    if request.method == 'GET':
        context = {
            'grades': grades,
            'academic_years': academic_years
        }
        return render(request, 'hod_template/admin_view_attendance.html', context)
        
    elif request.method == 'POST':
        # Get filter parameters
        grade_id = request.POST.get('grade')
        stream_id = request.POST.get('stream')
        academic_year_id = request.POST.get('academic_year')
        
        # Validate input
        if not grade_id or not academic_year_id:
            messages.error(request, "Please select both grade and academic year")
            return redirect('admin_view_attendance')
            
        try:
            grade = Grades.objects.get(id=grade_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        except (Grades.DoesNotExist, AcademicYear.DoesNotExist):
            messages.error(request, "Invalid selection")
            return redirect('admin_view_attendance')
        
        # Get streams for this grade
        streams = Streams.objects.filter(grade_id=grade)
        
        # Filter by stream if provided
        if stream_id:
            try:
                selected_stream = Streams.objects.get(id=stream_id, grade_id=grade)
                attendance_records = Attendance.objects.filter(
                    stream_id=selected_stream,
                    academic_year_id=academic_year
                ).order_by('-attendance_date')
            except Streams.DoesNotExist:
                messages.error(request, "Invalid stream selection")
                return redirect('admin_view_attendance')
        else:
            selected_stream = None
            attendance_records = Attendance.objects.filter(
                stream_id__grade_id=grade,
                academic_year_id=academic_year
            ).order_by('-attendance_date')
        
        # Get detailed attendance reports
        attendance_reports = {}
        for record in attendance_records:
            reports = AttendanceReport.objects.filter(
                attendance_id=record
            ).select_related('student_id', 'student_id__admin')
            attendance_reports[record.id] = reports
        
        context = {
            'grades': grades,
            'academic_years': academic_years,
            'streams': streams,
            'selected_grade': grade,
            'selected_stream': selected_stream,
            'selected_academic_year': academic_year,
            'attendance_records': attendance_records,
            'attendance_reports': attendance_reports
        }
        return render(request, 'hod_template/admin_view_attendance.html', context)
    
    else:
        messages.error(request, "Invalid Method")
        return redirect('admin_view_attendance')


def admin_edit_attendance_list(request):
    grades = Grades.objects.all()
    academic_years = AcademicYear.objects.all()
    
    if request.method == 'GET':
        context = {
            'grades': grades,
            'academic_years': academic_years
        }
        return render(request, 'hod_template/admin_edit_attendance_list.html', context)
        
    elif request.method == 'POST':
        grade_id = request.POST.get('grade')
        stream_id = request.POST.get('stream')
        academic_year_id = request.POST.get('academic_year')
        
        if not grade_id or not academic_year_id:
            messages.error(request, "Please select both grade and academic year")
            return redirect('admin_edit_attendance_list')
        
        try:
            grade = Grades.objects.get(id=grade_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        except (Grades.DoesNotExist, AcademicYear.DoesNotExist):
            messages.error(request, "Invalid selection")
            return redirect('admin_edit_attendance_list')
        
        streams = Streams.objects.filter(grade_id=grade)
        
        if stream_id:
            try:
                selected_stream = Streams.objects.get(id=stream_id, grade_id=grade)
                attendance_records = Attendance.objects.filter(
                    stream_id=selected_stream,
                    academic_year_id=academic_year
                ).order_by('-attendance_date')
            except Streams.DoesNotExist:
                messages.error(request, "Invalid stream selection")
                return redirect('admin_edit_attendance_list')
        else:
            selected_stream = None
            attendance_records = Attendance.objects.filter(
                stream_id__grade_id=grade,
                academic_year_id=academic_year
            ).order_by('-attendance_date')
        
        context = {
            'grades': grades,
            'academic_years': academic_years,
            'streams': streams,
            'selected_grade': grade,
            'selected_stream': selected_stream,
            'selected_academic_year': academic_year,
            'attendance_records': attendance_records
        }
        return render(request, 'hod_template/admin_edit_attendance_list.html', context)
    
    else:
        messages.error(request, "Invalid Method")
        return redirect('admin_edit_attendance_list')

@csrf_exempt
def admin_get_attendance_dates(request):
    stream = request.POST.get('stream_id')
    academic_year = request.POST.get('academic_year_id')
    
    try:
        stream_model = Streams.objects.get(id=stream)
        academic_year_model = AcademicYear.objects.get(id=academic_year)
        
        attendance = Attendance.objects.filter(
            stream_id=stream_model,
            academic_year_id=academic_year_model
        )
        
        attendance_list = []
        for attendance_single in attendance:
            data = {
                "id": attendance_single.id,
                "attendance_date": str(attendance_single.attendance_date),
                "created_at": str(attendance_single.created_at)
            }
            attendance_list.append(data)
        
        return JsonResponse({"status": "success", "attendance_dates": attendance_list})
        
    except ObjectDoesNotExist:
        return JsonResponse({"status": "error", "message": "Selected stream or academic year not found"})


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id, "name":student.student_id.first_name+" "+student.student_id.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')

def generate_face_encodings_for_existing_students(request):
    """
    Generate face encodings for all students who have profile pictures but no face encodings
    """
    if not request.user.is_authenticated or request.user.user_type != '1':
        return redirect('login')
        
    students = Students.objects.filter(profile_pic__isnull=False).exclude(
        id__in=FaceEncoding.objects.values_list('student_id', flat=True)
    )
    
    success_count = 0
    failed_count = 0
    no_face_count = 0
    
    for student in students:
        try:
            # Get the path to the profile picture
            image_path = student.profile_pic.path
            
            # Check if the file exists
            if not os.path.exists(image_path):
                failed_count += 1
                continue
                
            # Load the image and detect faces
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            
            if face_locations:
                # Get face encoding
                face_encoding = face_recognition.face_encodings(image, face_locations)[0]
                
                # Save face encoding
                FaceEncoding.objects.create(
                    student=student,
                    face_encoding=face_encoding.tobytes()
                )
                success_count += 1
            else:
                no_face_count += 1
        except Exception as e:
            print(f"Error processing student {student.id}: {str(e)}")
            failed_count += 1
    
    messages.success(request, f"Face encodings generated for {success_count} students. {no_face_count} had no detectable faces. {failed_count} failed.")
    return redirect('manage_student')

@csrf_exempt
@csrf_exempt
def get_streams_by_grade(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    
    grade_id = request.POST.get('grade_id')
    
    try:
        grade = Grades.objects.get(id=grade_id)
        streams = Streams.objects.filter(grade_id=grade)
        
        stream_list = []
        for stream in streams:
            stream_data = {
                'id': stream.id,
                'stream_name': stream.stream_name
            }
            stream_list.append(stream_data)
        
        return JsonResponse(json.dumps(stream_list), safe=False, content_type='application/json')
    
    except Exception as e:
        return JsonResponse(json.dumps([]), safe=False, content_type='application/json')


@csrf_exempt
def get_attendance_records(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    
    grade_id = request.POST.get('grade_id')
    stream_id = request.POST.get('stream_id')
    academic_year_id = request.POST.get('academic_year_id')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    try:
        academic_year = AcademicYear.objects.get(id=academic_year_id)
        
        # Base query - handle both specific stream and all streams in a grade
        if stream_id:
            # Get attendance for a specific stream
            stream = Streams.objects.get(id=stream_id)
            attendance_query = Attendance.objects.filter(
                stream_id=stream,
                academic_year_id=academic_year
            )
        else:
            # Get attendance for all streams in the selected grade
            grade = Grades.objects.get(id=grade_id)
            attendance_query = Attendance.objects.filter(
                stream_id__grade_id=grade,
                academic_year_id=academic_year
            )
        
        # Add date range filter if provided
        if start_date and end_date:
            attendance_query = attendance_query.filter(
                attendance_date__range=[start_date, end_date]
            )
        
        # Order by date
        attendance_query = attendance_query.order_by('-attendance_date')
        
        attendance_list = []
        for attendance in attendance_query:
            # Count present, absent, and leave students
            present_count = AttendanceReport.objects.filter(
                attendance_id=attendance,
                status='1'
            ).count()
            
            absent_count = AttendanceReport.objects.filter(
                attendance_id=attendance,
                status='0'
            ).count()
            
            leave_count = AttendanceReport.objects.filter(
                attendance_id=attendance,
                status='L'
            ).count()
            
            total_count = present_count + absent_count + leave_count
            present_percentage = (present_count / total_count * 100) if total_count > 0 else 0
            
            attendance_data = {
                'id': attendance.id,
                'attendance_date': attendance.attendance_date.strftime('%Y-%m-%d'),
                'stream_name': attendance.stream_id.stream_name,
                'academic_year': f"{academic_year.academic_start_year.strftime('%Y')} - {academic_year.academic_end_year.strftime('%Y')}",
                'present_count': present_count,
                'absent_count': absent_count,
                'leave_count': leave_count,
                'present_percentage': round(present_percentage, 1)
            }
            
            attendance_list.append(attendance_data)
        
        return JsonResponse(json.dumps(attendance_list), safe=False, content_type='application/json')
    
    except Exception as e:
        print(f"Error in get_attendance_records: {str(e)}")  # For debugging
        return JsonResponse(json.dumps([]), safe=False, content_type='application/json')

@csrf_exempt
def get_admin_attendance(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    
    grade_id = request.POST.get('grade')
    stream_id = request.POST.get('stream')
    academic_year_id = request.POST.get('academic_year')
    
    try:
        grade = Grades.objects.get(id=grade_id)
        academic_year = AcademicYear.objects.get(id=academic_year_id)
        
        if stream_id:
            attendance_records = Attendance.objects.filter(
                stream_id__id=stream_id,
                academic_year_id=academic_year
            ).order_by('-attendance_date')
        else:
            attendance_records = Attendance.objects.filter(
                stream_id__grade_id=grade,
                academic_year_id=academic_year
            ).order_by('-attendance_date')
        
        attendance_list = []
        for record in attendance_records:
            data = {
                'id': record.id,
                'attendance_date': record.attendance_date.strftime('%Y-%m-%d')
            }
            attendance_list.append(data)
        
        return JsonResponse(json.dumps(attendance_list), safe=False, content_type='application/json')
    
    except Exception as e:
        return JsonResponse(json.dumps([]), safe=False, content_type='application/json')

@csrf_exempt
def get_students_by_stream(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    
    stream_id = request.POST.get('stream_id')
    
    try:
        stream = Streams.objects.get(id=stream_id)
        students = Students.objects.filter(stream_id=stream)
        
        student_list = []
        for student in students:
            student_data = {
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'admission_number': student.admission_number if hasattr(student, 'admission_number') else 'N/A'
            }
            student_list.append(student_data)
        
        return JsonResponse(json.dumps(student_list), safe=False, content_type='application/json')
    
    except Exception as e:
        return JsonResponse(json.dumps([]), safe=False, content_type='application/json')



@csrf_exempt
def get_attendance_details(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    
    attendance_id = request.POST.get('attendance_id')
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        attendance_reports = AttendanceReport.objects.filter(attendance_id=attendance)
        
        report_list = []
        for report in attendance_reports:
            report_data = {
                'student_name': f"{report.student_id.first_name} {report.student_id.last_name}",
                'admission_number': report.student_id.admission_number,
                'status': report.status
            }
            report_list.append(report_data)
        
        return JsonResponse(json.dumps(report_list), safe=False, content_type='application/json')
    
    except Exception as e:
        return JsonResponse(json.dumps([]), safe=False, content_type='application/json')


@csrf_exempt
def save_face_dataset(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"})
    
    student_id = request.POST.get('student_id')
    images_json = request.POST.get('images')
    
    if not student_id or not images_json:
        return JsonResponse({"status": "error", "message": "Missing required data"})
    
    try:
        student = Students.objects.get(id=student_id)
        images = json.loads(images_json)
        
        for i, image_data in enumerate(images):
            # Save the image to a file
            image_data = image_data.split(',')[1]
            image_binary = base64.b64decode(image_data)
            
            # Create a unique filename
            filename = f'students/profile_pics/{student.admission_number}_{i+1}.jpg'
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the image
            with open(file_path, 'wb') as f:
                f.write(image_binary)
            
            # Generate face encoding
            image = face_recognition.load_image_file(file_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                # Save the face encoding
                face_encoding = face_encodings[0]
                FaceEncoding.objects.create(
                    student=student,
                    face_encoding=face_encoding.tobytes()
                )
        
        return JsonResponse({"status": "success", "message": "Face data saved successfully"})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error processing images: {str(e)}"})
    
def create_dataset(request, student_id):
    student = Students.objects.get(id=student_id)
    context = {
        'student': student
    }
    return render(request, 'hod_template/create_dataset_template.html', context)



def manage_student(request):
    students = Students.objects.all()
    print(f"Number of students: {students.count()}")
    grades = Grades.objects.all()
    streams = Streams.objects.all()
    
    # Check which students have face encodings
    for student in students:
        student.has_face_encoding = FaceEncoding.objects.filter(student=student).exists()
        
        # Get attendance statistics
        student.present_count = AttendanceReport.objects.filter(
            student_id=student,
            status='1'
        ).count()
        
        student.absent_count = AttendanceReport.objects.filter(
            student_id=student,
            status='0'
        ).count()
        
        # Get recent attendance (last 10 records)
        recent_reports = AttendanceReport.objects.filter(
            student_id=student
        ).order_by('-attendance_id__attendance_date')[:10]
        
        student.recent_attendance = []
        for report in recent_reports:
            student.recent_attendance.append({
                'date': report.attendance_id.attendance_date,
                'status': report.status
            })
    
    context = {
        "students": students,
        "grades": grades,
        "streams": streams
    }
    return render(request, "hod_template/manage_student_template.html", context)

# Add new view for exporting students
def export_students(request):
    if request.method != 'POST':
        return redirect('manage_student')
    
    student_ids = request.POST.get('student_ids').split(',')
    students = Students.objects.filter(id__in=student_ids)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Admission Number', 'First Name', 'Middle Name', 'Last Name', 
                    'Grade', 'Stream', 'Academic Year', 'Gender', 'Date of Birth',
                    'Parent Name', 'Address', 'Face Recognition Enabled'])
    
    for student in students:
        has_face_encoding = FaceEncoding.objects.filter(student=student).exists()
        writer.writerow([
            student.admission_number,
            student.first_name,
            student.middle_name,
            student.last_name,
            student.grade_id.grade_name,
            student.stream_id.stream_name,
            f"{student.academic_year_id.academic_start_year}/{student.academic_year_id.academic_end_year}",
            student.get_gender_display(),
            student.date_of_birth,
            student.parent_id.parent_name if student.parent_id else '',
            student.address,
            'Yes' if has_face_encoding else 'No'
        ])
    
    return response

# Add view for exporting all students
def export_all_students(request):
    students = Students.objects.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_students.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Admission Number', 'First Name', 'Middle Name', 'Last Name', 
                    'Grade', 'Stream', 'Academic Year', 'Gender', 'Date of Birth',
                    'Parent Name', 'Address', 'Face Recognition Enabled'])
    
    for student in students:
        has_face_encoding = FaceEncoding.objects.filter(student=student).exists()
        writer.writerow([
            student.admission_number,
            student.first_name,
            student.middle_name,
            student.last_name,
            student.grade_id.grade_name,
            student.stream_id.stream_name,
            f"{student.academic_year_id.academic_start_year}/{student.academic_year_id.academic_end_year}",
            student.get_gender_display(),
            student.date_of_birth,
            student.parent_id.parent_name if student.parent_id else '',
            student.address,
            'Yes' if has_face_encoding else 'No'
        ])
    
    return response

# Add view for bulk face enrollment
def bulk_face_enrollment(request):
    student_ids = request.GET.get('student_ids', '').split(',')
    
    if not student_ids or student_ids[0] == '':
        messages.error(request, "No students selected for face enrollment")
        return redirect('manage_student')
    
    # Store IDs in session for processing
    request.session['bulk_enrollment_ids'] = student_ids
    request.session['current_enrollment_index'] = 0
    
    # Redirect to the first student's face capture page
    return redirect('create_dataset_bulk')

# Add view for processing bulk dataset creation
def create_dataset_bulk(request):
    student_ids = request.session.get('bulk_enrollment_ids', [])
    current_index = request.session.get('current_enrollment_index', 0)
    
    if not student_ids or current_index >= len(student_ids):
        messages.success(request, "Completed face enrollment for all selected students")
        return redirect('manage_student')
    
    student_id = student_ids[current_index]
    student = Students.objects.get(id=student_id)
    
    context = {
        'student': student,
        'current': current_index + 1,
        'total': len(student_ids)
    }
    
    return render(request, 'hod_template/create_dataset_bulk_template.html', context)

# Add view for student attendance detail
def student_attendance_detail(request, student_id):
    student = Students.objects.get(id=student_id)
    
    # Get all attendance records for this student
    attendance_reports = AttendanceReport.objects.filter(
        student_id=student
    ).select_related('attendance_id').order_by('-attendance_id__attendance_date')
    
    # Calculate attendance statistics
    total_days = attendance_reports.count()
    present_days = attendance_reports.filter(status='1').count()
    absent_days = attendance_reports.filter(status='0').count()
    
    if total_days > 0:
        attendance_percentage = (present_days / total_days) * 100
    else:
        attendance_percentage = 0
    
    # Group attendance by month for chart
    months = {}
    for report in attendance_reports:
        month = report.attendance_id.attendance_date.strftime('%b %Y')
        if month not in months:
            months[month] = {'present': 0, 'absent': 0}
        
        if report.status:
            months[month]['present'] += 1
        else:
            months[month]['absent'] += 1
    
    context = {
        'student': student,
        'attendance_reports': attendance_reports,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': round(attendance_percentage, 2),
        'months': months
    }
    
    return render(request, 'hod_template/student_attendance_detail.html', context)

# Add these views to HodViews.py

@csrf_exempt
def save_face_image(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"})
    
    student_id = request.POST.get('student_id')
    image_data = request.POST.get('image_data')
    
    if not student_id or not image_data:
        return JsonResponse({"status": "error", "message": "Missing required data"})
    
    try:
        student = Students.objects.get(id=student_id)
    except Students.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Student not found"})
    
    try:
        # Save the image to a temporary file
        image_data = image_data.split(',')[1]
        image_binary = base64.b64decode(image_data)
        
        # Create a unique filename
        filename = f'face_images/{student.admission_number}_{uuid.uuid4().hex}.jpg'
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(image_binary)
        
        # Generate face encoding
        image = face_recognition.load_image_file(file_path)
        face_encodings = face_recognition.face_encodings(image)
        
        if not face_encodings:
            # Clean up the file if no face is detected
            os.remove(file_path)
            return JsonResponse({"status": "error", "message": "No face detected in the image"})
        
        # Save the face encoding
        face_encoding = face_encodings[0]
        FaceEncoding.objects.create(
            student=student,
            face_encoding=face_encoding.tobytes()
        )
        
        # Keep the image for reference
        return JsonResponse({"status": "success", "message": "Face encoding saved successfully"})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error processing image: {str(e)}"})

@csrf_exempt
def next_enrollment_student(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"})
    
    # Get the current enrollment session data
    student_ids = request.session.get('bulk_enrollment_ids', [])
    current_index = request.session.get('current_enrollment_index', 0)
    
    # Skip this student if requested
    skip = request.POST.get('skip') == 'true'
    
    # Move to the next student
    current_index += 1
    request.session['current_enrollment_index'] = current_index
    
    # Check if we've processed all students
    if current_index >= len(student_ids):
        # Clear the session data
        del request.session['bulk_enrollment_ids']
        del request.session['current_enrollment_index']
        
        return JsonResponse({
            "status": "success", 
            "message": "All students processed",
            "redirect": reverse('manage_student')
        })
    
    # Continue with the next student
    return JsonResponse({"status": "success", "message": "Moving to next student"})

def generate_face_encodings(request):
    """Generate face encodings for all students with profile pictures but no encodings"""
    students = Students.objects.filter(profile_pic__isnull=False)
    processed_count = 0
    error_count = 0
    
    for student in students:
        # Skip if already has encoding
        if FaceEncoding.objects.filter(student=student).exists():
            continue
        
        try:
            # Get the profile picture path
            profile_pic_path = os.path.join(settings.MEDIA_ROOT, str(student.profile_pic))
            
            # Generate face encoding
            image = face_recognition.load_image_file(profile_pic_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                # Save the face encoding
                face_encoding = face_encodings[0]
                FaceEncoding.objects.create(
                    student=student,
                    face_encoding=face_encoding.tobytes()
                )
                processed_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            print(f"Error processing {student.first_name} {student.last_name}: {str(e)}")
    
    if processed_count > 0:
        messages.success(request, f"Successfully generated face encodings for {processed_count} students")
    
    if error_count > 0:
        messages.warning(request, f"Failed to generate face encodings for {error_count} students")
    
    return redirect('manage_student')

import os
import pickle
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder

def train_model(request):
    """Train the face recognition model with all available encodings and save the model and encoder"""
    encodings = FaceEncoding.objects.all()
    if not encodings:
        messages.error(request, "No face encodings found to train the model.")
        return redirect('manage_student')

    X = []
    y = []

    for encoding in encodings:
        try:
            face_encoding = np.frombuffer(encoding.face_encoding)
            if face_encoding.shape[0] == 128:
                X.append(face_encoding)
                y.append(encoding.student.id)
        except Exception as e:
            encoding.delete()
            print(f"Error processing encoding for student {encoding.student.id}: {str(e)}")

    if not X or not y:
        messages.error(request, "No valid face encodings found to train the model.")
        return redirect('manage_student')

    X = np.array(X)
    y = np.array(y)

    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Train SVC model
    svc = SVC(kernel='linear', probability=True)
    svc.fit(X, y_encoded)

    # Save the model and encoder
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'face_recognition_data')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'svc.sav')
    classes_path = os.path.join(model_dir, 'classes.npy')

    with open(model_path, 'wb') as f:
        pickle.dump(svc, f)

    np.save(classes_path, label_encoder.classes_)

    messages.success(request, "Face recognition model trained and saved successfully.")
    return redirect('manage_student')

def admin_edit_attendance(request, attendance_id):
    """View for editing an attendance record"""
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        attendance_reports = AttendanceReport.objects.filter(attendance_id=attendance).order_by('student_id__first_name')
        
        # Calculate attendance statistics
        total_count = attendance_reports.count()
        present_count = attendance_reports.filter(status='1').count()
        absent_count = attendance_reports.filter(status='0').count()
        
        # Calculate percentages
        present_percentage = (present_count / total_count * 100) if total_count > 0 else 0
        absent_percentage = (absent_count / total_count * 100) if total_count > 0 else 0
        
        context = {
            'attendance': attendance,
            'attendance_reports': attendance_reports,
            'total_count': total_count,
            'present_count': present_count,
            'absent_count': absent_count,
            'present_percentage': present_percentage,
            'absent_percentage': absent_percentage
        }
        return render(request, 'hod_template/admin_edit_attendance.html', context)
    except Attendance.DoesNotExist:
        messages.error(request, "Attendance record not found")
        return redirect('admin_view_attendance')
    
def save_updated_attendance(request):
    """Save the updated attendance data"""
    if request.method != 'POST':
        messages.error(request, "Invalid Method")
        return redirect('admin_view_attendance')
    
    attendance_id = request.POST.get('attendance_id')
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        attendance_reports = AttendanceReport.objects.filter(attendance_id=attendance)
        
        # Track changes for logging
        changes_made = 0
        
        # Process each student's attendance status
        for report in attendance_reports:
            status_key = f'student_{report.id}'
            if status_key in request.POST:
                # Use '1' for present and '0' for absent instead of True/False
                new_status = '1' if request.POST.get(status_key) == 'present' else '0'
                
                # Update only if status has changed
                if report.status != new_status:
                    # Log the change - convert string status to boolean for the log
                    previous_status_bool = True if report.status == '1' else False
                    new_status_bool = True if new_status == '1' else False
                    
                    AttendanceChangeLog.objects.create(
                        attendance_report=report,
                        changed_by=request.user,
                        previous_status=previous_status_bool,
                        new_status=new_status_bool
                    )
                    
                    # Update the status
                    report.status = new_status
                    report.save()
                    changes_made += 1
        
        if changes_made > 0:
            messages.success(request, f"Attendance updated successfully. {changes_made} changes made.")
        else:
            messages.info(request, "No changes were made to the attendance record.")
            
        # Redirect back to the edit page to show the updated data
        return redirect('admin_edit_attendance', attendance_id=attendance_id)
        
    except Attendance.DoesNotExist:
        messages.error(request, "Attendance record not found")
        return redirect('admin_view_attendance')
    except Exception as e:
        messages.error(request, f"Error updating attendance: {str(e)}")
        return redirect('admin_edit_attendance', attendance_id=attendance_id)



def staff_profile(request):
    pass


def student_profile(requtest):
    pass

def parent_profile(requtest):
    pass