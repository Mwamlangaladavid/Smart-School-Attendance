class Staff {
  final int id;
  final String firstName;
  final String lastName;
  final String email;
  final String phone;
  final String address;
  final String dateJoined;

  Staff({
    required this.id,
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.phone,
    required this.address,
    required this.dateJoined,
  });

  factory Staff.fromJson(Map<String, dynamic> json) {
    return Staff(
      id: json['id'] ?? 0,
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      address: json['address'] ?? '',
      dateJoined: json['date_joined'] ?? '',
    );
  }
}

class Student {
  final int id;
  final String firstName;
  final String lastName;
  final String email;
  final String phone;
  final String address;
  final String course;
  final String dateJoined;

  Student({
    required this.id,
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.phone,
    required this.address,
    required this.course,
    required this.dateJoined,
  });

  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      id: json['id'] ?? 0,
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      address: json['address'] ?? '',
      course: json['course'] ?? '',
      dateJoined: json['date_joined'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'phone': phone,
      'address': address,
      'course': course,
      'date_joined': dateJoined,
    };
  }
}

class StaffLeaveRequest {
  final int id;
  final String staffName;
  final String leaveType;
  final String fromDate;
  final String toDate;
  final String reason;
  final String status;

  StaffLeaveRequest({
    required this.id,
    required this.staffName,
    required this.leaveType,
    required this.fromDate,
    required this.toDate,
    required this.reason,
    required this.status,
  });

  factory StaffLeaveRequest.fromJson(Map<String, dynamic> json) {
    return StaffLeaveRequest(
      id: json['id'] ?? 0,
      staffName: json['staff_name'] ?? '',
      leaveType: json['leave_type'] ?? '',
      fromDate: json['from_date'] ?? '',
      toDate: json['to_date'] ?? '',
      reason: json['reason'] ?? '',
      status: json['status'] ?? '',
    );
  }
}

class StudentFeedback {
  final int id;
  final String studentName;
  final String subject;
  final String feedback;
  final int rating;
  final String date;

  StudentFeedback({
    required this.id,
    required this.studentName,
    required this.subject,
    required this.feedback,
    required this.rating,
    required this.date,
  });

  factory StudentFeedback.fromJson(Map<String, dynamic> json) {
    return StudentFeedback(
      id: json['id'] ?? 0,
      studentName: json['student_name'] ?? '',
      subject: json['subject'] ?? '',
      feedback: json['feedback'] ?? '',
      rating: json['rating'] ?? 0,
      date: json['date'] ?? '',
    );
  }
}

class HODDashboardData {
  final DashboardStats stats;
  final List<Staff> recentStaff;
  final List<Student> recentStudents;

  HODDashboardData({
    required this.stats,
    required this.recentStaff,
    required this.recentStudents,
  });

  factory HODDashboardData.fromJson(Map<String, dynamic> json) {
    return HODDashboardData(
      stats: DashboardStats.fromJson(json['stats'] ?? {}),
      recentStaff: (json['recent_staff'] as List<dynamic>? ?? [])
          .map((item) => Staff.fromJson(item))
          .toList(),
      recentStudents: (json['recent_students'] as List<dynamic>? ?? [])
          .map((item) => Student.fromJson(item))
          .toList(),
    );
  }
}

class DashboardStats {
  final int totalStaff;
  final int totalStudents;
  final int pendingLeaveRequests;
  final int totalFeedback;

  DashboardStats({
    required this.totalStaff,
    required this.totalStudents,
    required this.pendingLeaveRequests,
    required this.totalFeedback,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalStaff: json['total_staff'] ?? 0,
      totalStudents: json['total_students'] ?? 0,
      pendingLeaveRequests: json['pending_leave_requests'] ?? 0,
      totalFeedback: json['total_feedback'] ?? 0,
    );
  }
}
