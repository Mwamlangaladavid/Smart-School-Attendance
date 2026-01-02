import os
import cv2
import dlib
import numpy as np
import face_recognition
import pickle
from imutils import face_utils
from imutils.face_utils import FaceAligner
from imutils.video import VideoStream
import imutils
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from .models import Students, Attendance, AttendanceReport, FaceEncoding, Streams, AcademicYear

# Create directory structure if it doesn't exist
os.makedirs('face_recognition_data/training_dataset', exist_ok=True)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import base64
import numpy as np

@csrf_exempt
def create_dataset_view(request, student_id):
    """
    View to capture face images sent from frontend and save to training dataset.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            image_data = data.get('image')
            if not image_data:
                return JsonResponse({'status': 'error', 'message': 'No image data provided'})

            format, imgstr = image_data.split(';base64,')
            img_bytes = base64.b64decode(imgstr)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            directory = f'face_recognition_data/training_dataset/{student_id}/'
            os.makedirs(directory, exist_ok=True)

            # Save image with incremental filename
            existing_files = [f for f in os.listdir(directory) if f.endswith('.jpg')]
            next_index = len(existing_files) + 1
            cv2.imwrite(f"{directory}/{next_index}.jpg", image)

            return JsonResponse({'status': 'success', 'message': f'Image {next_index} saved'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def train_model():
    """
    Train the face recognition model on all student datasets
    """
    training_dir = 'face_recognition_data/training_dataset'
    
    X = []  # Face encodings
    y = []  # Student IDs
    
    # Loop through each student directory
    for student_id in os.listdir(training_dir):
        curr_directory = os.path.join(training_dir, student_id)
        if not os.path.isdir(curr_directory):
            continue
            
        # Process each image in the student's directory
        for imagefile in [os.path.join(curr_directory, f) for f in os.listdir(curr_directory) if f.endswith('.jpg')]:
            image = cv2.imread(imagefile)
            try:
                # Get face encoding
                face_encoding = face_recognition.face_encodings(image)[0]
                X.append(face_encoding.tolist())
                y.append(student_id)
            except:
                # Remove problematic images
                os.remove(imagefile)
    
    # Convert lists to numpy arrays
    X = np.array(X)
    y = np.array(y)
    
    # Encode labels
    encoder = LabelEncoder()
    encoder.fit(y)
    y_encoded = encoder.transform(y)
    
    # Save the classes for later use
    np.save('face_recognition_data/classes.npy', encoder.classes_)
    
    # Train SVM classifier
    svc = SVC(kernel='linear', probability=True)
    svc.fit(X, y_encoded)
    
    # Save the trained model
    with open('face_recognition_data/svc.sav', 'wb') as f:
        pickle.dump(svc, f)
    
    return "Model trained successfully"

def mark_attendance_with_face(request, stream_id, academic_year_id):
    """
    Deprecated: This function uses blocking video stream and OpenCV GUI windows,
    which are not suitable for web applications and cause delays and failures.
    Please use the new API endpoint 'mark_attendance_api' in student_management_app/api/views.py
    with frontend webcam capture for better performance and reliability.
    """
    if request.method == 'GET':
        return render(request, 'staff_template/take_attendance_face_template.html', {
            'stream_id': stream_id,
            'academic_year_id': academic_year_id,
            'message': 'This attendance method is deprecated. Please use the new web-based attendance system.'
        })
    else:
        # For POST or other methods, redirect to staff home
        from django.contrib import messages
        messages.error(request, 'Deprecated attendance method. Please use the new web-based attendance system.')
        return redirect('staff_home')

@csrf_exempt
def generate_face_encodings(request):
    """
    Generate face encodings for all students with profile pictures
    """
    students = Students.objects.all()
    success_count = 0
    error_count = 0
    
    for student in students:
        if student.profile_pic:
            try:
                # Get the file path of the profile picture
                image_path = os.path.join(settings.MEDIA_ROOT, str(student.profile_pic))
                
                # Load the image and generate face encoding
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                
                if len(face_encodings) > 0:
                    # Save the face encoding to the database
                    face_encoding = face_encodings[0]
                    
                    # Check if encoding already exists
                    existing_encoding = FaceEncoding.objects.filter(student=student).first()
                    if existing_encoding:
                        existing_encoding.face_encoding = face_encoding.tobytes()
                        existing_encoding.save()
                    else:
                        FaceEncoding.objects.create(
                            student=student,
                            face_encoding=face_encoding.tobytes()
                        )
                    
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error processing {student.first_name} {student.last_name}: {str(e)}")
    
    messages.success(request, f"Successfully generated face encodings for {success_count} students. Failed for {error_count} students.")
    return redirect('manage_student')
