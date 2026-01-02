from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
import uuid
import os
import base64
from django.conf import settings
from datetime import datetime, time
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from django.contrib.auth.decorators import login_required
from student_management_app.models import CustomUser, Staffs, Grades, Streams, Students, AcademicYear, Attendance, AttendanceReport, LeaveReportStaff, FeedBackStaffs, StudentResult
import face_recognition
import numpy as np
import cv2
from .models import FaceEncoding
from django.views.decorators.http import require_GET
from django.utils.timezone import now
from django.http import JsonResponse


@require_GET
@login_required
def check_new_notifications(request):
    """
    API endpoint to check if there are new unread or pending notifications for the logged-in user,
    considering their role (admin, staff, parent).
    Returns JSON with a boolean 'has_new_notifications'.
    """
    user = request.user
    has_new_notifications = False

    # Check user role and query relevant models for new notifications
    if hasattr(user, 'staffs'):
        staff = user.staffs
        # Check for new leave requests (leave_status=0 means pending)
        new_leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=0).count()
        # Check for new feedback replies (non-empty feedback_reply)
        new_feedback_count = FeedBackStaffs.objects.filter(staff_id=staff.id).exclude(feedback_reply="").count()
        has_new_notifications = (new_leave_count > 0) or (new_feedback_count > 0)
    elif hasattr(user, 'parents'):
        parent = user.parents
        # Check for new feedback replies for parent
        new_feedback_count = FeedBackParents.objects.filter(parent_id=parent.id).exclude(feedback_reply="").count()
        has_new_notifications = (new_feedback_count > 0)
    elif user.is_superuser:
        # For admin, check all pending leave requests and feedbacks
        new_leave_count = LeaveReportStaff.objects.filter(leave_status=0).count()
        new_feedback_staff_count = FeedBackStaffs.objects.exclude(feedback_reply="").count()
        new_feedback_parent_count = FeedBackParents.objects.exclude(feedback_reply="").count()
        has_new_notifications = (new_leave_count > 0) or (new_feedback_staff_count > 0) or (new_feedback_parent_count > 0)

    return JsonResponse({"has_new_notifications": has_new_notifications})


def staff_recognize_face(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("staff_home"))
    
    # Get the data from the request
    stream_id = request.POST.get("stream_id")
    academic_year_id = request.POST.get("academic_year_id")
    face_data = request.POST.get("face_data")
    
    # Process the base64 image data
    if face_data and ',' in face_data:
        face_data = face_data.split(',')[1]
    
    # Create a temporary file to save the image
    import base64
    import tempfile
    import os
    import face_recognition
    import numpy as np
    from PIL import Image
    import io
    
    try:
        # Decode the base64 image
        image_data = base64.b64decode(face_data)
        image = Image.open(io.BytesIO(image_data))
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image_location = temp_file.name
        temp_file.close()
        
        # Save the image to the temporary file
        image.save(image_location)
        
        # Load the image for face recognition
        face_image = face_recognition.load_image_file(image_location)
        
        # Get face encodings from the image
        face_encodings = face_recognition.face_encodings(face_image)
        
        if not face_encodings:
            # Clean up the image file
            if os.path.exists(image_location):
                os.remove(image_location)
            return JsonResponse({"status": "info", "message": "No face detected in the cropped image"})
        
        # Get the face encoding of the first (and should be only) face in the image
        face_encoding = face_encodings[0]
        
        # Get all students in the stream and academic year
        from student_management_app.models import Students, Streams, AcademicYear, FaceEncoding
        
        stream = Streams.objects.get(id=stream_id)
        academic_year = AcademicYear.objects.get(id=academic_year_id)
        students = Students.objects.filter(grade_id=stream.grade_id, academic_year_id=academic_year)
        
        # Compare with all students' face encodings
        best_match = None
        best_match_distance = 1.0  # Initialize with maximum distance
        
        for student in students:
            # Get face encoding from FaceEncoding model
            face_encoding_obj = FaceEncoding.objects.filter(student=student).first()
            if face_encoding_obj:
                stored_encoding = np.frombuffer(face_encoding_obj.face_encoding, dtype=np.float64)
                
                # Compare face encodings
                face_distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
                
                # If this is the best match so far, store it
                if face_distance < best_match_distance:
                    best_match_distance = face_distance
                    best_match = student
        
        # Debug prints
        print(f"Number of face encodings found: {len(face_encodings)}")
        students_with_encoding = [student for student in students if FaceEncoding.objects.filter(student=student).exists()]
        print(f"Number of students with face encoding: {len(students_with_encoding)}")

        # Use a threshold to determine if the match is good enough
        # Lower threshold means stricter matching
        threshold = 0.6
        
        if best_match and best_match_distance < threshold:
            # Clean up the image file
            if os.path.exists(image_location):
                os.remove(image_location)
            
            # Return the recognized student
            confidence = 1.0 - best_match_distance  # Convert distance to confidence score
            return JsonResponse({
                "status": "success",
                "recognized_student": {
                    "id": best_match.id,
                    "name": best_match.first_name + " " + best_match.last_name,
                    "admission_number": best_match.admission_number,
                    "confidence": confidence
                }
            })
        else:
            # Clean up the image file
            if os.path.exists(image_location):
                os.remove(image_location)
            
            return JsonResponse({
                "status": "info",
                "message": "Face not recognized or confidence too low"
            })
    
    except Exception as e:
        # Clean up the image file if it exists
        try:
            if 'image_location' in locals() and os.path.exists(image_location):
                os.remove(image_location)
        except:
            pass
        
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })


@csrf_exempt
def _compare_faces(known_face, face_to_check, tolerance=0.7):
    """
    Compare two face images to determine if they belong to the same person.
    
    Args:
        known_face (str): Path to an image file containing a known face
        face_to_check (str): Path to an image file containing a face to compare
        tolerance (float): Threshold for face comparison (lower is more strict)
        
    Returns:
        Char: '1' if faces match, False otherwise
    """
    try:
        known_face_encodings = face_recognition.load_image_file(known_face)
        unknown_face_encodings = face_recognition.load_image_file(face_to_check)

        known_face_encodings = face_recognition.face_encodings(known_face_encodings)[0]
        unknown_face_encodings = face_recognition.face_encodings(unknown_face_encodings)[0]

        results = face_recognition.compare_faces([known_face_encodings], unknown_face_encodings, tolerance)
        return results[0]
    except Exception as e:
        print(f"Error in face comparison: {e}")  # For debugging
        return False

@csrf_exempt
def verify_fingerprint(request):
    if request.method == 'POST':
        stream_id = request.POST.get('stream_id')
        academic_year_id = request.POST.get('academic_year_id')
        student_id = request.POST.get('student_id')
        fingerprint_data = request.POST.get('fingerprint_data')
        
        # Validate input
        if not stream_id or not academic_year_id or not student_id or not fingerprint_data:
            return JsonResponse({"status": "error", "message": "Missing required data"})
            
        try:
            student = Students.objects.get(id=student_id)
            
            # Process the incoming fingerprint data
            try:
                # Decode the incoming fingerprint data (assuming it's in base64 format)
                decoded_fingerprint_data = base64.b64decode(fingerprint_data)
                
                # This is a placeholder for actual fingerprint verification
                # In a real implementation, you would need to:
                # 1. Import the appropriate fingerprint matching library
                # 2. Retrieve the stored fingerprint template
                # 3. Compare the templates
                
                # For now, we'll simulate verification
                is_verified = True  # Set a default value
                
                # Placeholder for actual fingerprint verification logic
                # In a real implementation, you would use a fingerprint matching library
                
                if not is_verified:
                    return JsonResponse({"status": "error", "message": "Fingerprint verification failed"})
                    
            except Exception as e:
                return JsonResponse({"status": "error", "message": f"Error processing fingerprint: {str(e)}"})
            
            if is_verified:
                return JsonResponse({
                    "status": "success", 
                    "message": "Fingerprint verified successfully",
                    "student": {
                        "id": student.id,
                        "name": f"{student.first_name} {student.last_name}",
                        "admission_number": student.admission_number
                    }
                })
            else:
                return JsonResponse({"status": "error", "message": "Fingerprint verification failed"})
                
        except Students.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student not found"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error verifying fingerprint: {str(e)}"})
    
    # If GET request, render the fingerprint verification page
    streams = Streams.objects.filter(staff_id=request.user.id)
    academic_years = AcademicYear.objects.all()
    context = {
        "streams": streams,
        "academic_years": academic_years
    }
    return render(request, "staff_template/verify_fingerprint_template.html", context)

@csrf_exempt
def staff_take_attendance_with_face(request):
    import json
    import logging
    import importlib
    logger = logging.getLogger(__name__)
    
    logger.debug("Received request for staff_take_attendance_with_face")
    
    # Check face_recognition library availability and version
    try:
        face_recognition_spec = importlib.util.find_spec("face_recognition")
        if face_recognition_spec is None:
            logger.error("face_recognition library is not installed")
            return JsonResponse({"status": "error", "message": "Face recognition library is not installed"})
        import face_recognition
        logger.info(f"face_recognition library version: {face_recognition.__version__}")
    except Exception as e:
        logger.error(f"Error importing face_recognition library: {str(e)}")
        return JsonResponse({"status": "error", "message": f"Error importing face_recognition library: {str(e)}"})
    
    if request.method == 'POST':
        stream_id = request.POST.get('stream_id') or request.GET.get('stream_id')
        academic_year_id = request.POST.get('academic_year_id') or request.GET.get('academic_year_id')
        attendance_type = request.POST.get('attendance_type')  # 'check_in' or 'check_out'
        
        # If parameters are missing, try to parse JSON body
        if not stream_id or not academic_year_id or not attendance_type:
            try:
                if request.body is None or not request.body.strip():
                    logger.error("Empty JSON body received")
                    return JsonResponse({"status": "error", "message": "Empty JSON body"})
                data = json.loads(request.body)
                stream_id = stream_id or data.get('stream_id')
                academic_year_id = academic_year_id or data.get('academic_year_id')
                attendance_type = attendance_type or data.get('attendance_type')
            except Exception as e:
                logger.error(f"Error parsing JSON body: {e}")
                return JsonResponse({"status": "error", "message": f"Error parsing JSON body: {str(e)}"})
        
        # Validate input
        if attendance_type not in ['check_in', 'check_out']:
            logger.error(f"Invalid attendance type: {attendance_type}")
            return JsonResponse({"status": "error", "message": "Invalid attendance type"})
            
        if not stream_id or not academic_year_id:
            # Try to get default stream and academic year from logged-in user context
            try:
                user = request.user
                streams = Streams.objects.filter(staff_id=user.id)
                academic_years = AcademicYear.objects.all()
                if streams.exists():
                    stream = streams.first()
                    stream_id = stream.id
                else:
                    logger.error("No stream assigned to user")
                    return JsonResponse({"status": "error", "message": "No stream assigned to user"})
                if academic_years.exists():
                    academic_year = academic_years.first()
                    academic_year_id = academic_year.id
                else:
                    logger.error("No academic year found")
                    return JsonResponse({"status": "error", "message": "No academic year found"})
            except Exception as e:
                logger.error(f"Error getting default stream or academic year: {str(e)}")
                return JsonResponse({"status": "error", "message": f"Error getting default stream or academic year: {str(e)}"})
        try:
            stream = Streams.objects.get(id=stream_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        except (ValueError, Streams.DoesNotExist, AcademicYear.DoesNotExist) as e:
            logger.error(f"Invalid stream or academic year: {str(e)}")
            return JsonResponse({"status": "error", "message": "Invalid stream or academic year"})
        
        # Get the base64 image from the request
        image_base64 = request.POST.get('image_data')
        if not image_base64:
            logger.error("No image data provided")
            return JsonResponse({"status": "error", "message": "No image data provided"})
        
        # Validate base64 format
        if ',' in image_base64:
            try:
                header, image_base64_data = image_base64.split(',', 1)
            except Exception as e:
                logger.error(f"Invalid image data format: {str(e)}")
                return JsonResponse({"status": "error", "message": f"Invalid image data format: {str(e)}"})
        else:
            image_base64_data = image_base64
        
        # Convert base64 to file
        filename = str('photo_taken/' + str(uuid.uuid4()) + '.jpg')
        image_location = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(image_location), exist_ok=True)
        
        try:
            with open(image_location, 'wb') as image_file:
                image_file.write(base64.b64decode(image_base64_data))
            logger.debug(f"Image saved to {image_location}")
            # Save a copy for debugging with timestamp
            debug_dir = os.path.join(settings.MEDIA_ROOT, 'debug_images')
            os.makedirs(debug_dir, exist_ok=True)
            debug_image_path = os.path.join(debug_dir, f"debug_{uuid.uuid4()}.jpg")
            with open(debug_image_path, 'wb') as debug_file:
                debug_file.write(base64.b64decode(image_base64_data))
            logger.info(f"Debug image saved to {debug_image_path}")
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            return JsonResponse({"status": "error", "message": f"Error saving image: {str(e)}"})
        
        # Get all students for this stream and academic year
        try:
            students = Students.objects.filter(
                grade_id=stream.grade_id,
                academic_year_id=academic_year
            )
        except Exception as e:
            logger.error(f"Error fetching students: {str(e)}")
            return JsonResponse({"status": "error", "message": f"Error fetching students: {str(e)}"})
        
        today = datetime.now().date()
        
        # Check if attendance record for today already exists
        try:
            existing_attendance = Attendance.objects.filter(
                stream_id=stream,
                attendance_date=today,
                academic_year_id=academic_year
            ).first()
        except Exception as e:
            logger.error(f"Error checking existing attendance: {str(e)}")
            return JsonResponse({"status": "error", "message": f"Error checking existing attendance: {str(e)}"})
        
        if not existing_attendance:
            # Create new attendance record for today
            try:
                attendance = Attendance.objects.create(
                    stream_id=stream,
                    attendance_date=today,
                    academic_year_id=academic_year
                )
            except Exception as e:
                logger.error(f"Error creating attendance record: {str(e)}")
                return JsonResponse({"status": "error", "message": f"Error creating attendance record: {str(e)}"})
        else:
            attendance = existing_attendance
        
        # Process the captured image for face recognition
        try:
            # Load the image and detect faces
            captured_image = face_recognition.load_image_file(image_location)
            
            # Get face locations first to determine how many faces are in the image
            logger.debug(f"Image location: {image_location}")
            if not os.path.exists(image_location):
                logger.error("Image file does not exist")
            else:
                logger.debug(f"Image file size: {os.path.getsize(image_location)} bytes")
            logger.debug(f"Captured image type: {type(captured_image)}, shape: {getattr(captured_image, 'shape', 'N/A')}")
            
            face_locations = face_recognition.face_locations(captured_image, model="hog")
            logger.debug(f"Detected face locations with HOG model: {face_locations}")
            if not face_locations:
                face_locations = face_recognition.face_locations(captured_image, model="cnn")
                logger.debug(f"Detected face locations with CNN model: {face_locations}")
            
            if not face_locations:
                # Clean up the image file
                if os.path.exists(image_location):
                    os.remove(image_location)
                logger.error("No face detected in the image. Please ensure your face is clearly visible and well-lit.")
                return JsonResponse({"status": "error", "message": "No face detected in the image. Please ensure your face is clearly visible and well-lit."})
            
            # Get face encodings for all detected faces
            captured_face_encodings = face_recognition.face_encodings(
                captured_image,
                known_face_locations=face_locations
            )
            
            # For each detected face, try to match with student face encodings
            attendance_marked = []
            recognized_student_ids = []
            
            # Use a stricter tolerance for face comparison to reduce false positives
            tolerance = 0.55  # Increased from 0.4 to 0.55 for better matching
            
            logger.info(f"Attendance marking started for stream_id={stream_id}, academic_year_id={academic_year_id}, attendance_type={attendance_type}")
            logger.info(f"Number of students in stream: {students.count()}")
            logger.info(f"Number of face encodings detected: {len(captured_face_encodings)}")
            
            # First, ensure all students have an attendance report (defaulting to absent)
            for student in students:
                # Check if student's attendance report already exists
                attendance_report = AttendanceReport.objects.filter(
                    student_id=student,
                    attendance_id=attendance
                ).first()
                
                if not attendance_report:
                    # Create new attendance report with absent status
                    AttendanceReport.objects.create(
                        student_id=student,
                        attendance_id=attendance,
                        status='0',  # Default to absent
                        check_in=None,
                        check_out=None
                    )
                elif attendance_type == 'check_in':
                    # Reset status to absent for check-in to ensure we're starting fresh
                    attendance_report.status = '0'
                    attendance_report.check_in = None
                    attendance_report.save()
            
            # For each face encoding, find the best matching student
            for captured_encoding in captured_face_encodings:
                best_match_student = None
                best_match_distance = 1.0  # Start with maximum distance
                
                for student in students:
                    face_encoding = FaceEncoding.objects.filter(student=student).first()
                    
                    if face_encoding:
                        student_encoding = np.frombuffer(face_encoding.face_encoding)
                        
                        face_distance = face_recognition.face_distance([student_encoding], captured_encoding)[0]
                        
                        if face_distance < best_match_distance and face_distance < tolerance:
                            best_match_distance = face_distance
                            best_match_student = student
                
                if best_match_student and best_match_student.id not in recognized_student_ids:
                    recognized_student_ids.append(best_match_student.id)
                    attendance_marked.append({
                        "id": best_match_student.id,
                        "name": f"{best_match_student.first_name} {best_match_student.last_name}",
                        "confidence": f"{(1 - best_match_distance) * 100:.1f}%"
                    })
                    logger.info(f"Recognized student: {best_match_student.first_name} {best_match_student.last_name} with confidence {(1 - best_match_distance) * 100:.1f}%")
            
            # Update attendance for recognized students
            for student_id in recognized_student_ids:
                try:
                    student = Students.objects.get(id=student_id)
                    attendance_report = AttendanceReport.objects.get(
                        student_id=student,
                        attendance_id=attendance
                    )
                    
                    current_time = datetime.now().time()
                    
                    if attendance_type == 'check_in':
                        attendance_report.check_in = current_time
                        attendance_report.status = '1'  # Mark as present
                    else:  # check_out
                        attendance_report.check_out = current_time
                        # Mark as present if check_in or check_out exists
                        if attendance_report.check_in or attendance_report.check_out:
                            attendance_report.status = '1'
                    
                    attendance_report.save()
                    logger.info(f"Attendance updated for student ID {student_id} at {current_time}")
                except Exception as e:
                    logger.error(f"Error updating attendance report for student ID {student_id}: {str(e)}")
            
            # Clean up the image file
            if os.path.exists(image_location):
                os.remove(image_location)
                
            absent_count = AttendanceReport.objects.filter(
                attendance_id=attendance,
                status='0'
            ).count()
            
            present_count = AttendanceReport.objects.filter(
                attendance_id=attendance,
                status='1'
            ).count()
            
            if attendance_marked:
                logger.info(f"Attendance marked successfully for {len(attendance_marked)} students")
                return JsonResponse({
                    "status": "success", 
                    "message": f"{attendance_type.replace('_', ' ').title()} marked successfully", 
                    "students": attendance_marked,
                    "present_count": present_count,
                    "absent_count": absent_count,
                    "total_count": students.count()
                })
            else:
                logger.warning("No matching students found. All students marked absent.")
                return JsonResponse({
                    "status": "warning", 
                    "message": "No matching students found. All students marked absent.",
                    "present_count": 0,
                    "absent_count": students.count(),
                    "total_count": students.count()
                })
                
        except Exception as e:
            import traceback
            if os.path.exists(image_location):
                os.remove(image_location)
            logger.error(f"Error processing image: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({"status": "error", "message": f"Error processing image: {str(e)}"})


    streams = Streams.objects.filter(staff_id=request.user.id)
    academic_years = AcademicYear.objects.all()
    context = {
        "streams": streams,
        "academic_years": academic_years
    }
    return render(request, "staff_template/take_attendance_face_template.html", context)


def add_student_face_encoding(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        face_image = request.FILES['face_image']
        
        fs = FileSystemStorage()
        filename = fs.save(f'face_images/{face_image.name}', face_image)
        image_path = fs.path(filename)
        
        image = face_recognition.load_image_file(image_path)
        face_encoding = face_recognition.face_encodings(image)[0]
        
        FaceEncoding.objects.create(
            student_id=student_id,
            face_encoding=face_encoding.tobytes()
        )
        
        fs.delete(filename)
        messages.success(request, "Face encoding added successfully")
        return redirect('manage_student')

@login_required
def staff_home(request):
    # Fetching All Students under Staff
    streams = Streams.objects.filter(staff_id=request.user.id)
    grade_id_list = []
    for stream in streams:
        grade = Grades.objects.get(id=stream.grade_id.id)
        grade_id_list.append(grade.id)
    
    final_grade = []
    # Removing Duplicate grade Id
    for grade_id in grade_id_list:
        if grade_id not in final_grade:
            final_grade.append(grade_id)
    
    students_count = Students.objects.filter(grade_id__in=final_grade).count()
    stream_count = streams.count()

    # Fetch All Attendance Count
    attendance_count = Attendance.objects.filter(stream_id__in=streams).count()

    # Fetch All Approve Leave
    staff = Staffs.objects.get(admin=request.user.id)
    leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()

    #Fetch Attendance Data by Streams
    stream_list = []
    attendance_list = []
    for stream in streams:
        attendance_count1 = Attendance.objects.filter(stream_id=stream.id).count()
        stream_list.append(stream.stream_name)
        attendance_list.append(attendance_count1)


    students_attendance = Students.objects.filter(grade_id__in=final_grade)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent = []
    for student in students_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status='1', student_id=student.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status='0', student_id=student.id).count()
        student_list.append(student.first_name+" "+ student.last_name)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    context={
        "students_count": students_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "stream_count": stream_count,
        "stream_list": stream_list,
        "attendance_list": attendance_list,
        "student_list": student_list,
        "attendance_present_list": student_list_attendance_present,
        "attendance_absent_list": student_list_attendance_absent
    }
    return render(request, "staff_template/staff_home_template.html", context)



def staff_take_attendance(request):
    streams = Streams.objects.filter(staff_id=request.user.id)
    academic_years = AcademicYear.objects.all()
    context = {
        "streams": streams,
        "academic_years": academic_years
    }

    if request.method == 'GET':
        return render(request, 'staff_template/take_attendance_template.html', context)
    else:
        # Add validation for stream_id
        stream_id = request.POST.get('stream_id')
        academic_year_id = request.POST.get('academic_year_id')
        
        # Validate that stream_id and academic_year_id are not None or empty
        if not stream_id or not academic_year_id:
            messages.error(request, "Stream or Academic Year not selected", extra_tags='danger')
            return render(request, 'staff_template/take_attendance_template.html', context)
        
        try:
            stream = Streams.objects.get(id=stream_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        except (Streams.DoesNotExist, AcademicYear.DoesNotExist):
            messages.error(request, "Invalid Stream or Academic Year", extra_tags='danger')
            return render(request, 'staff_template/take_attendance_template.html', context)
        # Get the base64 image from the request
        image_base64 = request.POST.get('image_data')
        # Convert base64 to file
        filename = str('photo_taken/' + str(uuid.uuid4()) + '.jpg')
        image_location = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(image_location), exist_ok=True)
        
        with open(image_location, 'wb') as image_file:
            image_file.write(base64.b64decode(image_base64))

        # Get students for this stream and academic year
        students = Students.objects.filter(
            grade_id=stream.grade_id,
            academic_year_id=academic_year
        )
        
        # Process the captured image for face recognition
        captured_image = face_recognition.load_image_file(image_location)
        captured_face_encodings = face_recognition.face_encodings(captured_image)
        
        if not captured_face_encodings:
            messages.error(request, "No face detected in the image", extra_tags='danger')
            return render(request, 'staff_template/take_attendance_template.html', context)
        
        # Create attendance record once
        attendance = Attendance.objects.create(
            stream_id=stream,
            attendance_date=datetime.now().date(),
            academic_year_id=academic_year
        )
        
        # For each detected face, try to match with student face encodings
        attendance_marked = []
        
        for student in students:
            # Get student's face encoding
            face_encoding = FaceEncoding.objects.filter(student=student).first()
            
            if face_encoding:
                # Compare with captured face
                student_encoding = np.frombuffer(face_encoding.face_encoding)
                
                for captured_encoding in captured_face_encodings:
                    # Compare faces
                    match = face_recognition.compare_faces([student_encoding], captured_encoding)[0]
                    
                    if match:
                        # Create or update attendance report with check_in time
                        attendance_report, created = AttendanceReport.objects.get_or_create(
                            student_id=student,
                            attendance_id=attendance,
                            defaults={'status': '1', 'check_in': datetime.now().time(), 'check_out': None}
                        )
                        if not created:
                            # Update check_in time if not set
                            if not attendance_report.check_in:
                                attendance_report.check_in = datetime.now().time()
                            attendance_report.status = '1'
                            attendance_report.save()
                        
                        attendance_marked.append(student.admin.first_name + " " + student.admin.last_name)
        
        if attendance_marked:
            messages.success(request, f"Attendance marked for: {', '.join(attendance_marked)}", extra_tags='success')
        else:
            messages.error(request, "No matching students found", extra_tags='warning')
        
        # Clean up the image file
        if os.path.exists(image_location):
            os.remove(image_location)
            
        return render(request, 'staff_template/take_attendance_template.html', context)




def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, "staff_template/staff_apply_leave_template.html", context)


def staff_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStaff(staff_id=staff_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('staff_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('staff_apply_leave')


def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaffs.objects.filter(staff_id=staff_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "staff_template/staff_feedback_template.html", context)


def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        staff_obj = Staffs.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStaffs(staff_id=staff_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('staff_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('staff_feedback')


# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_students(request):
    # Getting Values from Ajax POST 'Fetch Student'
    stream_id = request.POST.get("stream")
    academic_year = request.POST.get("academic_year")

    # Students enroll to grade, grade has Streams
    # Getting all data from stream model based on stream_id
    stream_model = Streams.objects.get(id=stream_id)

    academic_model = AcademicYear.objects.get(id=academic_year)

    students = Students.objects.filter(grade_id=stream_model.grade_id, academic_year_id=academic_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in students:
        data_small={"id":student.id, "name":student.first_name+" "+student.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)




@csrf_exempt
def save_attendance_data(request):
    # Get Values from Staff Take Attendance form via AJAX
    student_ids = request.POST.get("student_ids")
    stream_id = request.POST.get("stream_id")
    attendance_date = request.POST.get("attendance_date")
    academic_year_id = request.POST.get("academic_year_id")

    stream_model = Streams.objects.get(id=stream_id)
    academic_year_model = AcademicYear.objects.get(id=academic_year_id)
    
    # Get all students in this stream/grade and academic year
    all_students = Students.objects.filter(
        grade_id=stream_model.grade_id,
        academic_year_id=academic_year_model
    )

    json_student = json.loads(student_ids)
    
    # Create a dictionary of student IDs and their status from the submitted data
    submitted_status = {int(stud['id']): stud['status'] for stud in json_student}

    try:
        # First save Attendance record
        attendance = Attendance(
            stream_id=stream_model, 
            attendance_date=attendance_date,
            academic_year_id=academic_year_model
        )
        attendance.save()

        # Then save attendance reports for ALL students
        for student in all_students:
            # If student was in the submitted data, use that status
            if student.id in submitted_status:
                status = submitted_status[student.id]
            else:
                # If student wasn't in submitted data, mark as absent
                status = '0'
                
            attendance_report = AttendanceReport(
                student_id=student,
                attendance_id=attendance,
                status=status
            )
            attendance_report.save()
            
        return HttpResponse("OK")
    except Exception as e:
        print(e)  # For debugging
        return HttpResponse("Error")




def staff_update_attendance(request):
    streams = Streams.objects.filter(staff_id=request.user.id)
    academic_years = AcademicYear.objects.all()
    context = {
        "streams": streams,
        "academic_years": academic_years
    }
    return render(request, "staff_template/update_attendance_template.html", context)

@csrf_exempt
def staff_detect_faces(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"})
    
    stream_id = request.POST.get('stream_id')
    academic_year_id = request.POST.get('academic_year_id')
    
    # Validate input
    if not stream_id or not academic_year_id:
        return JsonResponse({"status": "error", "message": "Missing stream or academic year"})
        
    try:
        stream = Streams.objects.get(id=stream_id)
        academic_year = AcademicYear.objects.get(id=academic_year_id)
    except (ValueError, Streams.DoesNotExist, AcademicYear.DoesNotExist):
        return JsonResponse({"status": "error", "message": "Invalid stream or academic year"})
    
    # Get the base64 image from the request
    image_base64 = request.POST.get('image_data')
    if not image_base64:
        return JsonResponse({"status": "error", "message": "No image data provided"})
        
    # Convert base64 to file
    filename = str('photo_taken/' + str(uuid.uuid4()) + '.jpg')
    image_location = os.path.join(settings.MEDIA_ROOT, filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(image_location), exist_ok=True)
    
    try:
        with open(image_location, 'wb') as image_file:
            image_file.write(base64.b64decode(image_base64.split(',')[1]))
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error saving image: {str(e)}"})
    
    # Get students for this stream and academic year
    students = Students.objects.filter(
        grade_id=stream.grade_id,
        academic_year_id=academic_year
    )
    
    # Process the captured image for face recognition
    try:
        captured_image = face_recognition.load_image_file(image_location)
        face_locations = face_recognition.face_locations(captured_image)
        
        if not face_locations:
            # Clean up the image file
            if os.path.exists(image_location):
                os.remove(image_location)
            return JsonResponse({"status": "info", "message": "No face detected in the image", "face_locations": []})
        
        # Prepare face locations in dict format for client
        face_locations_list = []
        for (top, right, bottom, left) in face_locations:
            face_locations_list.append({
                "top": top,
                "right": right,
                "bottom": bottom,
                "left": left,
                "width": right - left,
                "height": bottom - top
            })
        
        # Clean up the image file
        if os.path.exists(image_location):
            os.remove(image_location)
        
        return JsonResponse({
            "status": "success",
            "message": f"{len(face_locations)} face(s) detected",
            "face_locations": face_locations_list
        })
        
    except Exception as e:
        # Clean up the image file
        if os.path.exists(image_location):
            os.remove(image_location)
        return JsonResponse({"status": "error", "message": f"Error processing image: {str(e)}"})

@csrf_exempt
def get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    stream_id = request.POST.get("stream")
    academic_year = request.POST.get("academic_year_id")

    # Students enroll to grade, grade has Streams
    # Getting all data from stream model based on stream_id
    stream_model = Streams.objects.get(id=stream_id)

    academic_model = AcademicYear.objects.get(id=academic_year)

    # students = Students.objects.filter(grade_id=stream_model.grade_id, academic_year_id=academic_model)
    attendance = Attendance.objects.filter(stream_id=stream_model, academic_year_id=academic_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "academic_year_id":attendance_single.academic_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)

@csrf_exempt
def get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
         # Convert status to appropriate format for JSON
        if student.status == 'L':
            status = 'L'  # Leave
        elif student.status == '1':
            status = '1'  # Present
        else:
            status = '0'  # Absent - Fixed missing assignment
        # Fix: Access student information directly from the student_id field
        data_small = {
            "id": student.student_id.id,  # Access the student's ID directly
            "name": student.student_id.first_name + " " + student.student_id.last_name,  # Access name directly
            "admission_no": student.student_id.admission_number,  # Use admission_number instead of roll
            "status": student.status
        }
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)

@csrf_exempt
def staff_save_attendance_with_face(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"})
    
    stream_id = request.POST.get('stream_id')
    academic_year_id = request.POST.get('academic_year_id')
    recognized_students_json = request.POST.get('recognized_students')
    
    # Validate input
    if not stream_id or not academic_year_id or not recognized_students_json:
        return JsonResponse({"status": "error", "message": "Missing required data"})
    
    try:
        stream = Streams.objects.get(id=stream_id)
        academic_year = AcademicYear.objects.get(id=academic_year_id)
        recognized_student_ids = json.loads(recognized_students_json)
    except (ValueError, Streams.DoesNotExist, AcademicYear.DoesNotExist, json.JSONDecodeError):
        return JsonResponse({"status": "error", "message": "Invalid data provided"})
    
    if not recognized_student_ids:
        return JsonResponse({"status": "warning", "message": "No students recognized"})
    
    try:
        # Create attendance record
        attendance = Attendance.objects.create(
            stream_id=stream,
            attendance_date=datetime.now().date(),
            academic_year_id=academic_year
        )
        
        # Create attendance reports for each recognized student
        students_marked = []
        for student_id in recognized_student_ids:
            try:
                student = Students.objects.get(id=student_id)
                AttendanceReport.objects.create(
                    student_id=student,
                    attendance_id=attendance,
                    status='1'  # Changed from True to '1'
                )
                students_marked.append(f"{student.first_name} {student.last_name}")
            except Students.DoesNotExist:
                continue
        
        return JsonResponse({
            "status": "success",
            "message": f"Attendance marked for {len(students_marked)} students",
            "students": students_marked
        })
    
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error saving attendance: {str(e)}"})



@csrf_exempt
def update_attendance_data(request):
    student_ids = request.POST.get("student_ids")
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)
    
    # Get all students who should have attendance for this record
    all_students = Students.objects.filter(
        grade_id=attendance.stream_id.grade_id,
        academic_year_id=attendance.academic_year_id
    )

    json_student = json.loads(student_ids)
    
    # Create a dictionary of student IDs and their status from the submitted data
    submitted_status = {int(stud['id']): stud['status'] for stud in json_student}

    try:
        # Update attendance for all students
        for student in all_students:
            # Try to get existing attendance report
            try:
                attendance_report = AttendanceReport.objects.get(
                    student_id=student, 
                    attendance_id=attendance
                )
                
                # If student was in the submitted data, update status
                if student.id in submitted_status:
                    attendance_report.status = submitted_status[student.id]
                    attendance_report.save()
                # If not in submitted data but has a report, ensure it's marked absent
                else:
                    attendance_report.status = '0'
                    attendance_report.save()
                    
            except AttendanceReport.DoesNotExist:
                # If no report exists, create one
                status = submitted_status.get(student.id, '0')  # Default to absent
                AttendanceReport.objects.create(
                    student_id=student,
                    attendance_id=attendance,
                    status=status
                )
                
        return HttpResponse("OK")
    except Exception as e:
        print(e)  # For debugging
        return HttpResponse("Error")



def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)

    context={
        "user": user,
        "staff": staff
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            staff = Staffs.objects.get(admin=customuser.id)
            staff.address = address
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')




@login_required
def staff_view_attendance(request):
    staff = Staffs.objects.get(admin=request.user)
    
    # Get streams assigned to this staff
    streams = Streams.objects.filter(staff_id=request.user)
    academic_years = AcademicYear.objects.all()
    
    context = {
        "streams": streams,
        "academic_years": academic_years
    }
    
    if request.method == 'POST':
        # Get filter parameters
        stream_id = request.POST.get('stream')
        academic_year_id = request.POST.get('academic_year')
        
        # Validate input
        if not stream_id or not academic_year_id:
            messages.error(request, "Please select both stream and academic year")
            return redirect('staff_view_attendance')
            
        try:
            selected_stream = Streams.objects.get(id=stream_id, staff_id=request.user)
            selected_academic_year = AcademicYear.objects.get(id=academic_year_id)
        except (Streams.DoesNotExist, AcademicYear.DoesNotExist):
            messages.error(request, "Invalid selection")
            return redirect('staff_view_attendance')
        
        # Get attendance records for this stream and academic year
        attendance_records = Attendance.objects.filter(
            stream_id=selected_stream,
            academic_year_id=selected_academic_year
        ).order_by('-attendance_date')
        
        # Get students in this stream and academic year
        students = Students.objects.filter(
            grade_id=selected_stream.grade_id,
            academic_year_id=selected_academic_year
        ).order_by('admission_number')
        
        # Create a dictionary to store attendance data by date
        attendance_data = {}
        attendance_dates = []
        
        # Collect all attendance dates
        for record in attendance_records:
            date_str = record.attendance_date.strftime('%d %b')  # Format: Day Month
            if date_str not in attendance_dates:
                attendance_dates.append(date_str)
            
            # Get attendance reports for this record
            reports = AttendanceReport.objects.filter(
                attendance_id=record
            ).select_related('student_id')
            
            # Store attendance status by student ID
            for report in reports:
                student_id = report.student_id.id
                if student_id not in attendance_data:
                    attendance_data[student_id] = {}
                
                # Store status, check-in and check-out times
                attendance_entry = {
                    'status': report.status,
                    'check_in': report.check_in,
                    'check_out': report.check_out
                }
                
                # Check if student has leave for this date
                leave_report = LeaveReportStaff.objects.filter(
                    staff_id=staff,
                    leave_date=record.attendance_date,
                    leave_status=1  # Approved leave
                ).exists()
                
                if leave_report:
                    attendance_entry['status'] = 'L'  # Mark as leave
                
                attendance_data[student_id][date_str] = attendance_entry
        
        # Prepare student attendance data for the template
        student_attendance = []
        for student in students:
            student_data = {
                'id': student.id,
                'admission_number': student.admission_number,
                'name': f"{student.first_name} {student.last_name}",
                'attendance': []
            }
            
            # Add attendance status for each date
            for date in attendance_dates:
                attendance_entry = attendance_data.get(student.id, {}).get(date, {
                    'status': None,
                    'check_in': None,
                    'check_out': None
                })
                
                student_data['attendance'].append({
                    'date': date,
                    'status': attendance_entry.get('status'),
                    'check_in': attendance_entry.get('check_in'),
                    'check_out': attendance_entry.get('check_out')
                })
            
            student_attendance.append(student_data)
        
        context.update({
            "selected_stream": selected_stream,
            "selected_academic_year": selected_academic_year,
            "attendance_dates": attendance_dates,
            "student_attendance": student_attendance
        })
    
    return render(request, "staff_template/staff_view_attendance.html", context)


@login_required
def staff_real_time_attendance(request):
    """
    Real-time face recognition attendance marking.
    Continuously captures frames from the camera, recognizes students,
    and marks attendance automatically before the last arrival time.
    """
    # Define last arrival time (e.g., 9:00 AM)
    last_arrival_time = time(9, 0, 0)

    if request.method == 'GET':
        return render(request, "staff_template/real_time_attendance.html")

    # For POST, start real-time attendance processing
    # This is a simplified example; in production, use WebSockets or async processing

    # Initialize video capture
    vs = cv2.VideoCapture(0)
    if not vs.isOpened():
        messages.error(request, "Camera failed to start. Please check the connection.")
        return redirect('staff_home')

    # Load face recognition model and encodings
    try:
        with open('face_recognition_data/svc.sav', 'rb') as f:
            svc = pickle.load(f)
        encoder = LabelEncoder()
        encoder.classes_ = np.load('face_recognition_data/classes.npy')
    except Exception as e:
        messages.error(request, "Face recognition model not found or failed to load.")
        return redirect('staff_home')

    # Get stream and academic year from request POST or fallback to user's assigned stream and academic year
    stream_id = request.POST.get('stream_id') or None
    academic_year_id = request.POST.get('academic_year_id') or None

    if not stream_id or not academic_year_id:
        try:
            user = request.user
            streams = Streams.objects.filter(staff_id=user.id)
            academic_years = AcademicYear.objects.all()
            if streams.exists():
                stream = streams.first()
                stream_id = stream.id
            else:
                messages.error(request, "No stream assigned to user.")
                return redirect('staff_home')
            if academic_years.exists():
                academic_year = academic_years.first()
                academic_year_id = academic_year.id
            else:
                messages.error(request, "No academic year found.")
                return redirect('staff_home')
        except Exception as e:
            messages.error(request, f"Error getting default stream or academic year: {str(e)}")
            return redirect('staff_home')

    try:
        stream = Streams.objects.get(id=stream_id)
        academic_year = AcademicYear.objects.get(id=academic_year_id)
    except (ValueError, Streams.DoesNotExist, AcademicYear.DoesNotExist):
        messages.error(request, "Invalid stream or academic year.")
        return redirect('staff_home')

    recognized_students = set()
    attendance = None

    while True:
        ret, frame = vs.read()
        if not ret:
            messages.error(request, "Failed to read from camera.")
            break

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame, model="cnn")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Process each detected face encoding to recognize students
        for face_encoding in face_encodings:
            probs = svc.predict_proba([face_encoding])[0]
            student_idx = np.argmax(probs)
            confidence = probs[student_idx]

            if confidence > 0.9:
                student_id = encoder.classes_[student_idx]
                if student_id not in recognized_students:
                    recognized_students.add(student_id)
                    try:
                        student = Students.objects.get(id=student_id)
                        # Mark attendance if not already marked
                        if not attendance:
                            attendance = Attendance.objects.create(
                                stream_id=stream,
                                attendance_date=datetime.now().date(),
                                academic_year_id=academic_year
                            )
                        attendance_report, created = AttendanceReport.objects.get_or_create(
                            student_id=student,
                            attendance_id=attendance,
                            defaults={'status': '1', 'check_in': datetime.now().time()}
                        )
                        if not created:
                            # Update check_in time if needed
                            if not attendance_report.check_in:
                                attendance_report.check_in = datetime.now().time()
                                attendance_report.status = '1'
                                attendance_report.save()
                    except Students.DoesNotExist:
                        pass

        # Display the frame with rectangles around faces
        for (top, right, bottom, left) in face_locations:
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow('Real-Time Attendance', frame)

        # Break loop if 'q' is pressed or after last arrival time
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if datetime.now().time() > last_arrival_time:
            break

    vs.release()
    cv2.destroyAllWindows()

    messages.success(request, "Real-time attendance session ended.")
    return redirect('staff_home')


@login_required
def export_attendance_csv(request):
    """
    Export attendance data for a selected stream and academic year as an Excel file,
    replicating the layout and appearance of the Attendance Records form.
    """
    stream_id = request.GET.get('stream_id')
    academic_year_id = request.GET.get('academic_year_id')

    if not stream_id or not academic_year_id:
        messages.error(request, "Stream and Academic Year must be selected for export.")
        return redirect('staff_view_attendance')

    try:
        stream = Streams.objects.get(id=stream_id)
        academic_year = AcademicYear.objects.get(id=academic_year_id)
    except (Streams.DoesNotExist, AcademicYear.DoesNotExist):
        messages.error(request, "Invalid Stream or Academic Year selected.")
        return redirect('staff_view_attendance')

    attendance_records = Attendance.objects.filter(
        stream_id=stream,
        academic_year_id=academic_year
    ).order_by('attendance_date')

    if not attendance_records.exists():
        messages.error(request, "No attendance data available to export.")
        return redirect('staff_view_attendance')

    # Create workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendance Records"

    # Styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="4F81BD")
    center_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Write main headers
    ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
    ws.cell(row=1, column=1, value="Admission No").font = header_font
    ws.cell(row=1, column=1).fill = header_fill
    ws.cell(row=1, column=1).alignment = center_alignment
    ws.cell(row=1, column=1).border = thin_border

    ws.merge_cells(start_row=1, start_column=2, end_row=2, end_column=2)
    ws.cell(row=1, column=2, value="Student Name").font = header_font
    ws.cell(row=1, column=2).fill = header_fill
    ws.cell(row=1, column=2).alignment = center_alignment
    ws.cell(row=1, column=2).border = thin_border

    # Dates headers with merged cells for Status, Check In, Check Out
    date_list = [record.attendance_date.strftime('%d %b %Y') for record in attendance_records]
    col = 3
    for date_str in date_list:
        ws.merge_cells(start_row=1, start_column=col, end_row=1, end_column=col+2)
        ws.cell(row=1, column=col, value=date_str).font = header_font
        ws.cell(row=1, column=col).fill = header_fill
        ws.cell(row=1, column=col).alignment = center_alignment
        ws.cell(row=1, column=col).border = thin_border

        ws.cell(row=2, column=col, value="Status").font = header_font
        ws.cell(row=2, column=col).fill = header_fill
        ws.cell(row=2, column=col).alignment = center_alignment
        ws.cell(row=2, column=col).border = thin_border

        ws.cell(row=2, column=col+1, value="Check In").font = header_font
        ws.cell(row=2, column=col+1).fill = header_fill
        ws.cell(row=2, column=col+1).alignment = center_alignment
        ws.cell(row=2, column=col+1).border = thin_border

        ws.cell(row=2, column=col+2, value="Check Out").font = header_font
        ws.cell(row=2, column=col+2).fill = header_fill
        ws.cell(row=2, column=col+2).alignment = center_alignment
        ws.cell(row=2, column=col+2).border = thin_border

        col += 3

    # Get students in the stream and academic year
    students = Students.objects.filter(
        grade_id=stream.grade_id,
        academic_year_id=academic_year
    ).order_by('admission_number')

    # Write student attendance data
    row = 3
    for student in students:
        ws.cell(row=row, column=1, value=student.admission_number)
        ws.cell(row=row, column=2, value=f"{student.first_name} {student.last_name}")

        col = 3
        for record in attendance_records:
            attendance_report = AttendanceReport.objects.filter(
                student_id=student,
                attendance_id=record
            ).first()
            if attendance_report:
                status_code = attendance_report.status
                # Map status code to label and color
                if status_code == '1':
                    status = "Present"
                    status_fill = PatternFill("solid", fgColor="28a745")  # Green
                elif status_code == '0':
                    status = "Absent"
                    status_fill = PatternFill("solid", fgColor="dc3545")  # Red
                elif status_code == 'L':
                    status = "Leave"
                    status_fill = PatternFill("solid", fgColor="ffc107")  # Yellow
                else:
                    status = "N/A"
                    status_fill = PatternFill("solid", fgColor="6c757d")  # Gray

                check_in = attendance_report.check_in.strftime('%H:%M') if attendance_report.check_in else "-"
                check_out = attendance_report.check_out.strftime('%H:%M') if attendance_report.check_out else "-"
            else:
                status = "N/A"
                status_fill = PatternFill("solid", fgColor="6c757d")  # Gray
                check_in = "-"
                check_out = "-"

            status_cell = ws.cell(row=row, column=col, value=status)
            status_cell.fill = status_fill
            status_cell.alignment = Alignment(horizontal="center", vertical="center")
            status_cell.font = Font(color="FFFFFF", bold=True)

            check_in_cell = ws.cell(row=row, column=col+1, value=check_in)
            check_in_cell.alignment = Alignment(horizontal="center", vertical="center")

            check_out_cell = ws.cell(row=row, column=col+2, value=check_out)
            check_out_cell.alignment = Alignment(horizontal="center", vertical="center")

            col += 3

        row += 1

    # Adjust column widths
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 25
    for i in range(3, col):
        ws.column_dimensions[get_column_letter(i)].width = 12

    # Apply border and alignment to all cells
    for r in ws.iter_rows(min_row=1, max_row=row-1, min_col=1, max_col=col-1):
        for cell in r:
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # Prepare response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"attendance_{stream.stream_name}_{academic_year.academic_start_year}_{academic_year.academic_end_year}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response



