from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import datetime

class AcademicYear(models.Model):
    id = models.AutoField(primary_key=True)
    academic_start_year = models.DateField()
    academic_end_year = models.DateField()
    objects = models.Manager()

class CustomUser(AbstractUser):
    user_type_data = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)

class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Grades(models.Model):
    id = models.AutoField(primary_key=True)
    grade_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Streams(models.Model):
    id = models.AutoField(primary_key=True)
    stream_name = models.CharField(max_length=255)
    grade_id = models.ForeignKey(Grades, on_delete=models.CASCADE, default=1)
    staff_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Students(models.Model):
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    
    disability_choices = [
        ('None', 'None'),
        ('Physical', 'Physical'),
        ('Visual', 'Visual'),
        ('Hearing', 'Hearing'),
        ('Other', 'Other')
    ]

    id = models.AutoField(primary_key=True)
    admission_number = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=gender_choices)
    profile_pic = models.ImageField(upload_to='students/profile_pics/', null=True, blank=True)
    address = models.TextField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, default='Tanzanian')
    religion = models.CharField(max_length=100)
    disability = models.CharField(max_length=25, choices=disability_choices, default='None')
    grade_id = models.ForeignKey(Grades, on_delete=models.CASCADE)
    stream_id = models.ForeignKey(Streams, on_delete=models.CASCADE)
    academic_year_id = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

@receiver(pre_save, sender=Students)
def generate_admission_number(sender, instance, **kwargs):
    if not instance.admission_number:
        year = datetime.datetime.now().year
        count = Students.objects.filter(created_at__year=year).count() + 1
        instance.admission_number = f"{year}/{str(count).zfill(3)}"

class Parents(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

# Add to existing models.py
class FaceEncoding(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    face_encoding = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    stream_id = models.ForeignKey(Streams, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    academic_year_id = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class AttendanceReport(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, default='0')
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.student_id.first_name + " " + self.attendance_id.attendance_date.strftime('%Y-%m-%d')

class AttendanceChangeLog(models.Model):
    attendance_report = models.ForeignKey(AttendanceReport, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    previous_status = models.BooleanField()
    new_status = models.BooleanField()
    change_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attendance change for {self.attendance_report.student_id.first_name} on {self.attendance_report.attendance_id.attendance_date}"

class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class FeedBackParents(models.Model):
    id = models.AutoField(primary_key=True)
    parent_id = models.ForeignKey(Parents, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class StudentResult(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    stream_id = models.ForeignKey(Streams, on_delete=models.CASCADE)
    stream_exam_marks = models.FloatField(default=0)
    stream_assignment_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type == 2:
            Staffs.objects.create(admin=instance)
        if instance.user_type == 3:
            Students.objects.create(grade_id=Grades.objects.get(id=1), academic_year_id=AcademicYear.objects.get(id=1), address="", profile_pic="", gender="")
        
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:  # HOD
        instance.adminhod.save()
    elif instance.user_type == 2:  # Staff
        instance.staffs.save()
    # Only save parents if the relationship exists
    elif instance.user_type == 4 and hasattr(instance, 'parents'):  # Parent
        instance.parents.save()

@receiver(pre_save, sender=Staffs)
def generate_staff_id(sender, instance, **kwargs):
    if not instance.staff_id:
        # Exclude current instance if it exists (for updates)
        if instance.pk:
            staff_ids = Staffs.objects.filter(staff_id__startswith='st').exclude(pk=instance.pk).values_list('staff_id', flat=True)
        else:
            staff_ids = Staffs.objects.filter(staff_id__startswith='st').values_list('staff_id', flat=True)
        max_id_num = 0
        for sid in staff_ids:
            try:
                num_part = int(sid[2:])
                if num_part > max_id_num:
                    max_id_num = num_part
            except (ValueError, TypeError):
                continue
        new_id = max_id_num + 1 if max_id_num > 0 else 1
        instance.staff_id = f"st{new_id}"
