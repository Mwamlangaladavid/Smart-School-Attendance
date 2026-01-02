from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AdminHOD, Staffs, Grades, Streams, Students, Attendance, AttendanceReport, LeaveReportStudent, LeaveReportStaff, FeedBackParents, FeedBackStaffs, NotificationStudent, NotificationStaffs, StudentResult, AcademicYear

admin.site.register(CustomUser, UserAdmin)
admin.site.register(AdminHOD)
admin.site.register(Staffs)
admin.site.register(Grades)
admin.site.register(Streams)
admin.site.register(Students)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(LeaveReportStudent)
admin.site.register(LeaveReportStaff)
admin.site.register(FeedBackParents)
admin.site.register(FeedBackStaffs)
admin.site.register(NotificationStudent)
admin.site.register(NotificationStaffs)
admin.site.register(StudentResult)
admin.site.register(AcademicYear)
