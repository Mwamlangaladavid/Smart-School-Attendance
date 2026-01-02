from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from student_management_app.EmailBackEnd import EmailBackEnd
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.base import ContentFile
import base64
import cv2
import numpy as np
import face_recognition
import pickle
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
from student_management_app.models import Students, Attendance, AttendanceReport, Streams, AcademicYear

from rest_framework.parsers import JSONParser
from django.http import JsonResponse
import json
from json.decoder import JSONDecodeError

import os
import pickle
import numpy as np
import cv2
import face_recognition
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
from student_management_app.models import Students, Attendance, AttendanceReport, Streams, AcademicYear
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
import base64
import json
from json.decoder import JSONDecodeError
import logging

# Load model and encoder globally to avoid reloading on every request
model_path = 'face_recognition_data/svc.sav'
classes_path = 'face_recognition_data/classes.npy'

logger = logging.getLogger(__name__)

try:
    with open(model_path, 'rb') as f:
        svc = pickle.load(f)
    encoder = LabelEncoder()
    encoder.classes_ = np.load(classes_path)
    logger.info("Model and encoder loaded successfully")
except Exception as e:
    svc = None
    encoder = None
    logger.error(f"Failed to load model or encoder: {str(e)}")

@api_view(['POST'])
@parser_classes([JSONParser])
@permission_classes([AllowAny])
@csrf_exempt
def staff_recognize_face(request):
    """
    API endpoint to recognize a single cropped face image sent from frontend.
    """
    logger.debug("Received request for staff_recognize_face")

    if svc is None or encoder is None:
        error_message = "Model or encoder not loaded. Please train the model first."
        logger.error(error_message)
        return Response({'status': 'error', 'message': error_message}, status=500)

    if not request.content_type or 'application/json' not in request.content_type:
        logger.error("Invalid Content-Type header. Expected application/json.")
        return Response({'status': 'error', 'message': 'Content-Type must be application/json'}, status=400)

    data = None
    try:
        data = request.data
    except JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        logger.error(f"Raw request body: {request.body}")
        return Response({'status': 'error', 'message': f'JSON decode error: {str(e)}'}, status=400)

    if not data or data == {}:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception as e:
            logger.error(f"Manual JSON parse error: {str(e)}")
            logger.error(f"Raw request body: {request.body}")
            return Response({'status': 'error', 'message': 'Empty or invalid JSON or form body'}, status=400)

    image_data = data.get('face_data')
    stream_id = data.get('stream_id')
    academic_year_id = data.get('academic_year_id')

    if not image_data or not stream_id or not academic_year_id:
        logger.error("Missing required parameters for face recognition")
        return Response({'status': 'error', 'message': 'Missing required parameters'}, status=400)

    try:
        format, imgstr = image_data.split(';base64,')
        img_bytes = base64.b64decode(imgstr)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        face_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        face_encodings = face_recognition.face_encodings(face_image)
        if len(face_encodings) == 0:
            logger.warning("No face encoding found in the image")
            return Response({'status': 'error', 'message': 'No face found'}, status=404)

        face_encoding = face_encodings[0]
        probs = svc.predict_proba([face_encoding])[0]
        student_idx = np.argmax(probs)
        confidence = probs[student_idx]

        if confidence > 0.9:
            student_id = encoder.classes_[student_idx]
            try:
                student = Students.objects.get(id=student_id)
                student_data = {
                    'id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'admission_number': getattr(student, 'admission_number', ''),
                    'confidence': confidence
                }
                return Response({'status': 'success', 'recognized_student': student_data})
            except Students.DoesNotExist:
                logger.warning(f"Student with id {student_id} does not exist")
                return Response({'status': 'error', 'message': 'Student not found'}, status=404)
        else:
            logger.info("Face not recognized with sufficient confidence")
            return Response({'status': 'error', 'message': 'Face not recognized'}, status=404)

    except Exception as e:
        import traceback
        logger.error(f"Exception during face recognition: {str(e)}")
        logger.error(traceback.format_exc())
        logger.error(f"Raw request body: {request.body}")
        return Response({'status': 'error', 'message': str(e)}, status=500)

from django.db import transaction

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from student_management_app.models import Streams, AcademicYear, Students, Attendance, AttendanceReport

@csrf_exempt
def mark_attendance_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            stream_id = data.get('stream_id')
            academic_year_id = data.get('academic_year_id')
            recognized_students = data.get('recognized_students', [])
            attendance_type = data.get('attendance_type', 'check_in')  # default to check_in if not provided

            if not stream_id or not academic_year_id:
                return JsonResponse({'status': 'error', 'message': 'Missing stream_id or academic_year_id'})

            stream = Streams.objects.get(id=stream_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)

            # Create attendance record for today
            today = datetime.now().date()
            attendance, created = Attendance.objects.get_or_create(
                stream_id=stream,
                attendance_date=today,
                academic_year_id=academic_year
            )

            # Get all students in the stream and academic year
            all_students = Students.objects.filter(
                grade_id=stream.grade_id,
                academic_year_id=academic_year
            )

            # Create or update attendance reports for all students
            for student in all_students:
                status = '1' if student.id in recognized_students else '0'
                attendance_report, created = AttendanceReport.objects.get_or_create(
                    student_id=student,
                    attendance_id=attendance,
                    defaults={'status': status}
                )
                if not created:
                    attendance_report.status = status

                # Set check_in or check_out time based on attendance_type
                current_time = datetime.now().time()
                if attendance_type == 'check_in':
                    attendance_report.check_in = current_time
                elif attendance_type == 'check_out':
                    attendance_report.check_out = current_time

                attendance_report.save()

            return JsonResponse({'status': 'success', 'message': 'Attendance marked successfully'})
        except Streams.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid stream_id'})
        except AcademicYear.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid academic_year_id'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = EmailBackEnd.authenticate(request, username=email, password=password)
    
    if user is not None:
        login(request, user)
        return Response({
            'status': 'success',
            'user_type': user.user_type,
            'token': 'your-token-logic-here'
        })
    return Response({'status': 'error'}, status=401)

@api_view(['GET'])
def get_student_info(request):
    # Add your student info logic here
    return Response({'status': 'success'})
