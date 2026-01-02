from rest_framework import serializers
from student_management_app.models import CustomUser, Students, Parents, AttendanceReport, LeaveReportStudent, FeedBackParent, StudentResult

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'user_type']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = ['id', 'admin', 'gender', 'grade_id', 'stream_id', 'session_year_id']

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parents
        fields = ['id', 'admin', 'student']

class AttendanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceReport
        fields = ['id', 'student_id', 'attendance_id', 'status']

class LeaveReportStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveReportStudent
        fields = ['id', 'student_id', 'leave_date', 'leave_message', 'leave_status']

class FeedBackParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBackParent
        fields = ['id', 'student_id', 'feedback', 'feedback_reply']

class StudentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentResult
        fields = ['id', 'student_id', 'subject_id', 'subject_exam_marks', 'subject_assignment_marks']
