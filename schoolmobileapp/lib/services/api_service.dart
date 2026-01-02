import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static String _cachedIP = '';
  static String? _token;

  static Future<String> get baseUrl async {
    if (_cachedIP.isEmpty) {
      final prefs = await SharedPreferences.getInstance();
      _cachedIP = prefs.getString('server_ip') ?? _getDefaultIP();
    }
    return 'http://192.168.36.124:8000';
  }

  static String _getDefaultIP() {
    if (Platform.isAndroid) {
      return '10.0.2.2';
    } else if (Platform.isIOS) {
      return 'localhost';
    }
    return 'localhost';
  }

  static void clearCachedIP() {
    _cachedIP = '';
  }

  static void setToken(String token) {
    _token = token;
  }

  static Map<String, String> _getHeaders() {
    Map<String, String> headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (_token != null) {
      headers['Authorization'] = 'Token $_token';
    }

    return headers;
  }

  static Future<Map<String, dynamic>> testConnectionDetailed() async {
    final url = await baseUrl;

    List<String> testEndpoints = ['$url/', '$url/admin/', '$url/api/'];

    Map<String, dynamic> results = {
      'success': false,
      'url': url,
      'tests': <Map<String, dynamic>>[],
      'error': '',
    };

    for (String endpoint in testEndpoints) {
      try {
        final response = await http
            .get(Uri.parse(endpoint), headers: _getHeaders())
            .timeout(const Duration(seconds: 10));

        Map<String, dynamic> testResult = {
          'endpoint': endpoint,
          'status': response.statusCode,
          'success': response.statusCode >= 200 && response.statusCode < 400,
          'error': null,
        };

        results['tests'].add(testResult);

        if (testResult['success']) {
          results['success'] = true;
        }
      } catch (e) {
        Map<String, dynamic> testResult = {
          'endpoint': endpoint,
          'status': 0,
          'success': false,
          'error': e.toString(),
        };

        results['tests'].add(testResult);
      }
    }

    if (!results['success']) {
      results['error'] =
          'All connection attempts failed. Check IP address and server status.';
    }

    return results;
  }

  static Future<bool> testConnection() async {
    final result = await testConnectionDetailed();
    return result['success'];
  }

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    return await loginWithUserType(email, password, 'hod');
  }

  static Future<Map<String, dynamic>> loginWithUserType(
    String email,
    String password,
    String userType,
  ) async {
    try {
      final url = await baseUrl;

      // Use the working API endpoint pattern
      String endpoint =
          '$url/api/mobile/login/'; // This should work like hod/login did

      final requestBody = {
        'email': email.trim(),
        'password': password,
        'user_type': userType.toLowerCase(),
      };

      // Don't send Authorization header for login
      Map<String, String> headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

      final response = await http
          .post(
            Uri.parse(endpoint),
            headers: headers,
            body: jsonEncode(requestBody),
          )
          .timeout(const Duration(seconds: 15));

      print('Response Status: ${response.statusCode}');
      print('Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        if (data['success'] == true) {
          if (data['token'] != null) {
            setToken(data['token']);
          }
          return {'success': true, 'data': data};
        } else {
          return {'success': false, 'error': data['error'] ?? 'Login failed'};
        }
      } else {
        return {
          'success': false,
          'error': 'Login failed: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getHODDashboard() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/hod/dashboard/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('HOD Dashboard API Response Status: ${response.statusCode}');
      print('HOD Dashboard API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Invalid response structure',
            };
          }
        } else {
          return {'success': true, 'data': responseData};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch dashboard data: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in getHODDashboard: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getAllStaff() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/staff/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Staff API Response Status: ${response.statusCode}');
      print('Staff API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to load staff. Status: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in getAllStaff: $e');
      return {'success': false, 'error': 'Network error: $e.toString()}'};
    }
  }

  static Future<Map<String, dynamic>> addStaff(
    Map<String, dynamic> staffData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/staff/add/'),
            headers: _getHeaders(),
            body: jsonEncode(staffData),
          )
          .timeout(const Duration(seconds: 15));

      print('Add Staff API Response Status: ${response.statusCode}');
      print('Add Staff API Response Body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to add staff: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in addStaff: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getAllStudents() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/students/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Students API Response Status: ${response.statusCode}');
      print('Students API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch student data: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Students API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Student Feedback APIs
  static Future<Map<String, dynamic>> getStudentFeedback() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/student-feedback/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Student Feedback API Response Status: ${response.statusCode}');
      print('Student Feedback API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch student feedback: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Student Feedback API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> submitStudentFeedback(
    Map<String, dynamic> feedbackData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/student-feedback/submit/'),
            headers: _getHeaders(),
            body: jsonEncode(feedbackData),
          )
          .timeout(const Duration(seconds: 15));

      print(
        'Submit Student Feedback API Response Status: ${response.statusCode}',
      );
      print('Submit Student Feedback API Response Body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to submit feedback: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in submitStudentFeedback: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getFeedbackByStudent(
    int studentId,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(
            Uri.parse('$url/api/student-feedback/student/$studentId/'),
            headers: _getHeaders(),
          )
          .timeout(const Duration(seconds: 15));

      print(
        'Get Feedback by Student API Response Status: ${response.statusCode}',
      );
      print('Get Feedback by Student API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch student feedback: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Get Feedback by Student API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> addStudent(
    Map<String, dynamic> studentData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/students/add/'),
            headers: _getHeaders(),
            body: jsonEncode(studentData),
          )
          .timeout(const Duration(seconds: 15));

      print('Add Student API Response Status: ${response.statusCode}');
      print('Add Student API Response Body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to add student: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in addStudent: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getParentChildren() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/parent/children/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Parent Children API Response Status: ${response.statusCode}');
      print('Parent Children API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true) {
            return {'success': true, 'data': responseData['data'] ?? []};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch children data: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in getParentChildren: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getParentDashboard() async {
    try {
      final url = await baseUrl;

      print('Fetching Parent Dashboard from: $url/api/parent/dashboard/');
      print('Using headers: ${_getHeaders()}');

      final response = await http
          .get(Uri.parse('$url/api/parent/dashboard/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 30));

      print('Parent Dashboard API Response Status: ${response.statusCode}');
      print('Parent Dashboard API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Invalid response from server',
            };
          }
        } else {
          return {
            'success': false,
            'error': 'Unexpected response format from server',
          };
        }
      } else if (response.statusCode == 401) {
        return {
          'success': false,
          'error': 'Authentication failed. Please login again.',
        };
      } else if (response.statusCode == 403) {
        return {
          'success': false,
          'error': 'Access denied. Parent privileges required.',
        };
      } else {
        return {
          'success': false,
          'error': 'Server error: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in getParentDashboard: $e');
      if (e.toString().contains('TimeoutException')) {
        return {
          'success': false,
          'error': 'Request timeout. Please check your internet connection.',
        };
      }
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }

  // Parent Apply Leave API
  static Future<Map<String, dynamic>> parentApplyLeave(
    Map<String, dynamic> leaveData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/parent/apply-leave/'),
            headers: _getHeaders(),
            body: jsonEncode(leaveData),
          )
          .timeout(const Duration(seconds: 15));

      print('Parent Apply Leave API Response Status: ${response.statusCode}');
      print('Parent Apply Leave API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return responseData;
      } else {
        return {
          'success': false,
          'error': 'Failed to apply leave: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in parentApplyLeave: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getStaffDashboard() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/staff/dashboard/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Staff Dashboard API Response Status: ${response.statusCode}');
      print('Staff Dashboard API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Invalid response structure',
            };
          }
        } else {
          return {'success': true, 'data': responseData};
        }
      } else {
        return {
          'success': false,
          'error':
              'Failed to fetch staff dashboard data: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in getStaffDashboard: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getParentNotifications() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(
            Uri.parse('$url/api/parent/notifications/'),
            headers: _getHeaders(),
          )
          .timeout(const Duration(seconds: 15));

      print('Parent Notifications API Response Status: ${response.statusCode}');
      print('Parent Notifications API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true) {
            return {'success': true, 'data': responseData['data'] ?? []};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch notifications: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in getParentNotifications: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> markNotificationAsRead(
    int notificationId,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/notifications/mark-read/'),
            headers: _getHeaders(),
            body: jsonEncode({'notification_id': notificationId}),
          )
          .timeout(const Duration(seconds: 15));

      print('Mark Notification Read Response Status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {
          'success': responseData['success'] ?? true,
          'message': responseData['message'] ?? 'Notification marked as read',
        };
      } else {
        return {
          'success': false,
          'error':
              'Failed to mark notification as read: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in markNotificationAsRead: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> markAllNotificationsAsRead() async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/notifications/mark-all-read/'),
            headers: _getHeaders(),
          )
          .timeout(const Duration(seconds: 15));

      print(
        'Mark All Notifications Read Response Status: ${response.statusCode}',
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {
          'success': responseData['success'] ?? true,
          'message':
              responseData['message'] ?? 'All notifications marked as read',
        };
      } else {
        return {
          'success': false,
          'error':
              'Failed to mark all notifications as read: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in markAllNotificationsAsRead: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> deleteNotification(
    int notificationId,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .delete(
            Uri.parse('$url/api/notifications/delete/$notificationId/'),
            headers: _getHeaders(),
          )
          .timeout(const Duration(seconds: 15));

      print('Delete Notification Response Status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {
          'success': responseData['success'] ?? true,
          'message': responseData['message'] ?? 'Notification deleted',
        };
      } else {
        return {
          'success': false,
          'error': 'Failed to delete notification: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in deleteNotification: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getParentAttendanceData(
    String period,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(
            Uri.parse('$url/api/parent/attendance/?period=$period'),
            headers: _getHeaders(),
          )
          .timeout(const Duration(seconds: 15));

      print('Parent Attendance API Response Status: ${response.statusCode}');
      print('Parent Attendance API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch attendance data: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in getParentAttendanceData: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getLeaveRequests() async {
    try {
      final url = await baseUrl;

      print('Fetching leave requests from: $url/api/leave-requests/');
      print('Using headers: ${_getHeaders()}');

      final response = await http
          .get(Uri.parse('$url/api/leave-requests/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Leave Requests API Response Status: ${response.statusCode}');
      print('Leave Requests API Response Body: ${response.body}');
      print('Response Content Length: ${response.body.length}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData.containsKey('success')) {
            if (responseData['success'] == true) {
              return {'success': true, 'data': responseData['data'] ?? []};
            } else {
              return {
                'success': false,
                'error': responseData['error'] ?? 'Unknown error from server',
              };
            }
          } else if (responseData.containsKey('results')) {
            return {'success': true, 'data': responseData['results'] ?? []};
          } else {
            return {
              'success': true,
              'data': [responseData],
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          print('Unexpected response format: ${responseData.runtimeType}');
          return {
            'success': false,
            'error': 'Unexpected response format: ${responseData.runtimeType}',
          };
        }
      } else {
        return {
          'success': false,
          'error':
              'Failed to fetch leave requests. Status: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Leave Requests API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> updateLeaveRequest(
    dynamic requestId,
    String status,
  ) async {
    try {
      final url = await baseUrl;

      dynamic id = requestId;
      if (requestId is String) {
        id = int.tryParse(requestId) ?? requestId;
      }

      print('Updating leave request ID: $id with status: $status');

      final requestBody = {'request_id': id, 'status': status.toLowerCase()};

      final response = await http
          .post(
            Uri.parse('$url/api/leave-requests/update/'),
            headers: _getHeaders(),
            body: jsonEncode(requestBody),
          )
          .timeout(const Duration(seconds: 15));

      print('Update Leave Request API Response Status: ${response.statusCode}');
      print('Update Leave Request API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData.containsKey('success')) {
            if (responseData['success'] == true) {
              return {'success': true, 'data': responseData};
            } else {
              return {
                'success': false,
                'error':
                    responseData['error'] ?? 'Failed to update leave request',
              };
            }
          } else {
            return {'success': true, 'data': responseData};
          }
        } else {
          return {'success': true, 'data': responseData};
        }
      } else {
        return {
          'success': false,
          'error':
              'Failed to update leave request. Status: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in updateLeaveRequest: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static void logout() {
    _token = null;
  }

  // Additional utility methods for better API handling
  static Future<Map<String, dynamic>> makeGetRequest(String endpoint) async {
    try {
      final url = await baseUrl;
      final response = await http
          .get(Uri.parse('$url$endpoint'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('GET $endpoint - Status: ${response.statusCode}');
      print('GET $endpoint - Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Request failed with status: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in GET $endpoint: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> makePostRequest(
    String endpoint,
    Map<String, dynamic> data,
  ) async {
    try {
      final url = await baseUrl;
      final response = await http
          .post(
            Uri.parse('$url$endpoint'),
            headers: _getHeaders(),
            body: jsonEncode(data),
          )
          .timeout(const Duration(seconds: 15));

      print('POST $endpoint - Status: ${response.statusCode}');
      print('POST $endpoint - Body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Request failed with status: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in POST $endpoint: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Subject Management APIs
  static Future<Map<String, dynamic>> getAllSubjects() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/subjects/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Subjects API Response Status: ${response.statusCode}');
      print('Subjects API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch subjects: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Subjects API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> addSubject(
    Map<String, dynamic> subjectData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/subjects/add/'),
            headers: _getHeaders(),
            body: jsonEncode(subjectData),
          )
          .timeout(const Duration(seconds: 15));

      print('Add Subject API Response Status: ${response.statusCode}');
      print('Add Subject API Response Body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to add subject: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in addSubject: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Attendance Management APIs
  static Future<Map<String, dynamic>> getAttendanceData() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/attendance/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Attendance API Response Status: ${response.statusCode}');
      print('Attendance API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch attendance data: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Attendance API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> markAttendance(
    Map<String, dynamic> attendanceData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/attendance/mark/'),
            headers: _getHeaders(),
            body: jsonEncode(attendanceData),
          )
          .timeout(const Duration(seconds: 15));

      print('Mark Attendance API Response Status: ${response.statusCode}');
      print('Mark Attendance API Response Body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to mark attendance: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in markAttendance: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> applyStudentLeave(
    String leaveDate,
    String leaveMessage,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/parent/apply-leave/'),
            headers: _getHeaders(),
            body: jsonEncode({
              'leave_date': leaveDate,
              'leave_msg': leaveMessage,
            }),
          )
          .timeout(const Duration(seconds: 15));

      print('Apply Leave API Response Status: ${response.statusCode}');
      print('Apply Leave API Response Body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to apply for leave: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in applyStudentLeave: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Notification APIs
  static Future<Map<String, dynamic>> getNotifications() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/notifications/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Notifications API Response Status: ${response.statusCode}');
      print('Notifications API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else if (responseData is List) {
          return {'success': true, 'data': responseData};
        } else {
          return {'success': false, 'error': 'Unexpected response format'};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch notifications: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Notifications API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> sendNotification(
    Map<String, dynamic> notificationData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/notifications/send/'),
            headers: _getHeaders(),
            body: jsonEncode(notificationData),
          )
          .timeout(const Duration(seconds: 15));

      print('Send Notification API Response Status: ${response.statusCode}');
      print('Send Notification API Response Body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to send notification: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in sendNotification: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  //staff calls//
  static Future<Map<String, dynamic>> submitAttendance(
    List<Map<String, dynamic>> attendanceData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/staff/attendance/submit/'),
            headers: _getHeaders(),
            body: jsonEncode({'attendance_data': attendanceData}),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to submit attendance: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> submitLeaveRequest(
    Map<String, dynamic> leaveData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .post(
            Uri.parse('$url/api/staff/leave/apply/'),
            headers: _getHeaders(),
            body: jsonEncode(leaveData),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to submit leave request: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Profile Management APIs
  static Future<Map<String, dynamic>> getUserProfile() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/profile/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Profile API Response Status: ${response.statusCode}');
      print('Profile API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch profile: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Profile API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> updateProfile(
    Map<String, dynamic> profileData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .put(
            Uri.parse('$url/api/profile/update/'),
            headers: _getHeaders(),
            body: jsonEncode(profileData),
          )
          .timeout(const Duration(seconds: 15));

      print('Update Profile API Response Status: ${response.statusCode}');
      print('Update Profile API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to update profile: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in updateProfile: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Reports APIs
  static Future<Map<String, dynamic>> getReports(String reportType) async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(
            Uri.parse('$url/api/reports/$reportType/'),
            headers: _getHeaders(),
          )
          .timeout(const Duration(seconds: 15));

      print('Reports API Response Status: ${response.statusCode}');
      print('Reports API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData is Map<String, dynamic>) {
          if (responseData['success'] == true && responseData['data'] != null) {
            return {'success': true, 'data': responseData['data']};
          } else {
            return {
              'success': false,
              'error': responseData['error'] ?? 'Unknown error',
            };
          }
        } else {
          return {'success': true, 'data': responseData};
        }
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch reports: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Reports API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Settings APIs
  static Future<Map<String, dynamic>> getSettings() async {
    try {
      final url = await baseUrl;

      final response = await http
          .get(Uri.parse('$url/api/settings/'), headers: _getHeaders())
          .timeout(const Duration(seconds: 15));

      print('Settings API Response Status: ${response.statusCode}');
      print('Settings API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch settings: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Settings API Error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> updateSettings(
    Map<String, dynamic> settingsData,
  ) async {
    try {
      final url = await baseUrl;

      final response = await http
          .put(
            Uri.parse('$url/api/settings/update/'),
            headers: _getHeaders(),
            body: jsonEncode(settingsData),
          )
          .timeout(const Duration(seconds: 15));

      print('Update Settings API Response Status: ${response.statusCode}');
      print('Update Settings API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': 'Failed to update settings: ${response.statusCode}',
        };
      }
    } catch (e) {
      print('Error in updateSettings: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
}
