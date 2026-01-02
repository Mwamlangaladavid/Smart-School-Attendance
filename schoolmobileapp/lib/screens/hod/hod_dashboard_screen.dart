import 'package:flutter/material.dart';
import '../../../services/api_service.dart';
import '../../../models/hod_models.dart';
import 'edit_attendance_screen.dart';
import 'manage_parents_screen.dart';
import 'manage_staff_screen.dart';
import 'manage_student_screen.dart' show ManageStudentsScreen;
import 'leave_requests_screen.dart';
import 'add_staff_screen.dart';
import 'add_student_screen.dart';
import 'parent_feedback_screen.dart';
import 'student_leave_screen.dart';
import 'add_parent_screen.dart';
import 'add_grade_screen.dart';
import 'view_attendance_screen.dart';
import 'manage_grades_screen.dart';
import 'add_stream_screen.dart';
import 'manage_streams_screen.dart';
import 'add_academic_year_screen.dart';
import 'manage_academic_year_screen.dart';

class HODDashboardScreen extends StatefulWidget {
  const HODDashboardScreen({super.key});

  @override
  State<HODDashboardScreen> createState() => _HODDashboardScreenState();
}

class _HODDashboardScreenState extends State<HODDashboardScreen> {
  HODDashboardData? _dashboardData;
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    final result = await ApiService.getHODDashboard();

    setState(() {
      _isLoading = false;
      if (result['success']) {
        _dashboardData = result['data'];
      } else {
        _error = result['error'];
      }
    });
  }

  // Fixed logout method
  Future<void> _handleLogout() async {
    final shouldLogout = await _showLogoutDialog();
    if (shouldLogout == true) {
      try {
        // Clear token and navigate to login
        ApiService.logout();

        // Navigate back to login screen and clear all previous routes
        if (mounted) {
          Navigator.of(context).pushNamedAndRemoveUntil(
            '/', // Assuming '/' is your login route
            (route) => false,
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Logout failed: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  Future<bool?> _showLogoutDialog() {
    return showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Confirm Logout'),
          content: const Text('Are you sure you want to logout?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: const Text('Logout'),
            ),
          ],
        );
      },
    );
  }

  void _navigateToAddStaff() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const AddStaffScreen()),
    );
  }

  void _navigateToStaffLeave() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const LeaveRequestsScreen()),
    );
  }

  void _navigateToStudentLeave() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const StudentLeaveScreen()),
    );
  }

  void _navigateToAddParent() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const AddParentScreen()),
    );
  }

  void _navigateToManageParents() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ManageParentsScreen()),
    );
  }

  void _navigateToParentFeedback() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ParentFeedbackScreen()),
    );
  }

  void _navigateToAddGrade() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const AddGradeScreen()),
    );
  }

  void _navigateToManageGrades() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ManageGradesScreen()),
    );
  }

  void _navigateToAddStream() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const AddStreamScreen()),
    );
  }

  void _navigateToManageStreams() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ManageStreamsScreen()),
    );
  }

  void _navigateToAddAcademicYear() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const AddAcademicYearScreen()),
    );
  }

  void _navigateToManageAcademicYear() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ManageAcademicYearScreen()),
    );
  }

  void _navigateToViewAttendance() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ViewAttendanceScreen()),
    );
  }

  void _navigateToEditAttendance() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const EditAttendanceScreen()),
    );
  }

  void _navigateToSettings() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Settings screen is under development'),
        backgroundColor: Colors.orange,
      ),
    );
  }

  void _navigateToProfile() {
    // TODO: Create ProfileScreen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Profile screen is under development'),
        backgroundColor: Colors.orange,
      ),
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            Text(
              title,
              style: TextStyle(fontSize: 14, color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionCard(
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 32, color: color),
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecentActivity() {
    if (_dashboardData == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Recent Activity', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 16),

        // Pending Leave Requests
        if (_dashboardData!.recentStaff.isNotEmpty) ...[
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.pending_actions, color: Colors.orange[700]),
                      const SizedBox(width: 8),
                      const Text(
                        'Recent Staff',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ...(_dashboardData!.recentStaff
                          .take(3)
                          .map(
                            (staff) => ListTile(
                              dense: true,
                              title: Text(
                                '${staff.firstName} ${staff.lastName}',
                              ),
                              subtitle: Text(staff.email),
                              trailing: const Icon(
                                Icons.arrow_forward_ios,
                                size: 16,
                              ),
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) =>
                                        const ManageStaffScreen(),
                                  ),
                                );
                              },
                            ),
                          ))
                      .toList(),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],

        // Recent Students
        if (_dashboardData!.recentStudents.isNotEmpty) ...[
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.school, color: Colors.blue[700]),
                      const SizedBox(width: 8),
                      const Text(
                        'Recent Students',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ...(_dashboardData!.recentStudents
                          .take(3)
                          .map(
                            (student) => ListTile(
                              dense: true,
                              title: Text(
                                '${student.firstName} ${student.lastName}',
                              ),
                              subtitle: Text(
                                '${student.course} - ${student.email}',
                              ),
                              trailing: const Icon(
                                Icons.arrow_forward_ios,
                                size: 16,
                              ),
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) =>
                                        const ManageStudentsScreen(),
                                  ),
                                );
                              },
                            ),
                          ))
                      .toList(),
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('HOD Dashboard'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDashboardData,
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'profile':
                  _navigateToProfile();
                  break;
                case 'logout':
                  _handleLogout();
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'profile',
                child: Row(
                  children: [
                    Icon(Icons.person),
                    SizedBox(width: 8),
                    Text('Profile'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout, color: Colors.red),
                    SizedBox(width: 8),
                    Text('Logout', style: TextStyle(color: Colors.red)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      drawer: _buildDrawer(),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error.isNotEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error, size: 64, color: Colors.red[300]),
                  const SizedBox(height: 16),
                  Text(_error),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loadDashboardData,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: _loadDashboardData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Welcome Card
                    Card(
                      color: Theme.of(context).colorScheme.primaryContainer,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Row(
                          children: [
                            Icon(
                              Icons.dashboard,
                              size: 40,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Welcome, Head of Department',
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleLarge
                                        ?.copyWith(
                                          color: Theme.of(
                                            context,
                                          ).colorScheme.primary,
                                        ),
                                  ),
                                  Text(
                                    'Manage your institution efficiently',
                                    style: TextStyle(
                                      color: Theme.of(context)
                                          .colorScheme
                                          .primary
                                          .withValues(alpha: 0.7),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 24),

                    // Statistics Cards
                    Text(
                      'Overview',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    GridView.count(
                      crossAxisCount: 2,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      childAspectRatio: 1.2,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                      children: [
                        _buildStatCard(
                          'Total Students',
                          '${_dashboardData?.stats.totalStudents ?? 0}',
                          Icons.school,
                          Colors.blue,
                        ),
                        _buildStatCard(
                          'Total Staff',
                          '${_dashboardData?.stats.totalStaff ?? 0}',
                          Icons.people,
                          Colors.green,
                        ),
                        _buildStatCard(
                          'Pending Requests',
                          '${_dashboardData?.stats.pendingLeaveRequests ?? 0}',
                          Icons.pending_actions,
                          Colors.orange,
                        ),
                        _buildStatCard(
                          'Total Feedback',
                          '${_dashboardData?.stats.totalFeedback ?? 0}',
                          Icons.feedback,
                          Colors.purple,
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // Quick Actions
                    Text(
                      'Quick Actions',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    GridView.count(
                      crossAxisCount: 3,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      childAspectRatio: 1,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      children: [
                        _buildQuickActionCard(
                          'Manage Staff',
                          Icons.people_outline,
                          Colors.blue,
                          () => Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const ManageStaffScreen(),
                            ),
                          ),
                        ),
                        _buildQuickActionCard(
                          'Manage Students',
                          Icons.school_outlined,
                          Colors.green,
                          () => Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) =>
                                  const ManageStudentsScreen(),
                            ),
                          ),
                        ),
                        _buildQuickActionCard(
                          'Leave Requests',
                          Icons.pending_actions,
                          Colors.orange,
                          () => Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const LeaveRequestsScreen(),
                            ),
                          ),
                        ),
                        _buildQuickActionCard(
                          'Manage Parents',
                          Icons.family_restroom,
                          Colors.teal,
                          _navigateToManageParents,
                        ),
                        _buildQuickActionCard(
                          'View Attendance',
                          Icons.calendar_today,
                          Colors.indigo,
                          _navigateToViewAttendance,
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // Recent Activity
                    _buildRecentActivity(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: Colors.white,
                  child: Icon(
                    Icons.person,
                    size: 40,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'HOD Dashboard',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Text(
                  'Head of Department',
                  style: TextStyle(color: Colors.white70, fontSize: 14),
                ),
              ],
            ),
          ),

          // Dashboard Home
          ListTile(
            leading: const Icon(Icons.dashboard),
            title: const Text('Home'),
            onTap: () {
              Navigator.pop(context);
            },
          ),

          // Staff Management Section
          ExpansionTile(
            leading: const Icon(Icons.people),
            title: const Text('Staff Management'),
            children: [
              ListTile(
                leading: const Icon(Icons.person_add),
                title: const Text('Add Staff'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToAddStaff();
                },
              ),
              ListTile(
                leading: const Icon(Icons.manage_accounts),
                title: const Text('Manage Staff'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const ManageStaffScreen(),
                    ),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.calendar_today),
                title: const Text('Staff Leave'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToStaffLeave();
                },
              ),
            ],
          ),

          // Student Management Section
          ExpansionTile(
            leading: const Icon(Icons.school),
            title: const Text('Student Management'),
            children: [
              ListTile(
                leading: const Icon(Icons.person_add),
                title: const Text('Add Student'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const AddStudentScreen(),
                    ),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.groups),
                title: const Text('Manage Students'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const ManageStudentsScreen(),
                    ),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.calendar_today),
                title: const Text('Student Leave'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToStudentLeave();
                },
              ),
            ],
          ),

          // Parent Management Section
          ExpansionTile(
            leading: const Icon(Icons.family_restroom),
            title: const Text('Parent Management'),
            children: [
              ListTile(
                leading: const Icon(Icons.person_add),
                title: const Text('Add Parent'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToAddParent();
                },
              ),
              ListTile(
                leading: const Icon(Icons.supervisor_account),
                title: const Text('Manage Parents'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToManageParents();
                },
              ),
              ListTile(
                leading: const Icon(Icons.feedback),
                title: const Text('Parent Feedback'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToParentFeedback();
                },
              ),
            ],
          ),

          // Class Management Section
          ExpansionTile(
            leading: const Icon(Icons.class_),
            title: const Text('Class Management'),
            children: [
              ListTile(
                leading: const Icon(Icons.add),
                title: const Text('Add Grade'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToAddGrade();
                },
              ),
              ListTile(
                leading: const Icon(Icons.grade),
                title: const Text('Manage Grades'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToManageGrades();
                },
              ),
              ListTile(
                leading: const Icon(Icons.add),
                title: const Text('Add Stream'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToAddStream();
                },
              ),
              ListTile(
                leading: const Icon(Icons.stream),
                title: const Text('Manage Streams'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToManageStreams();
                },
              ),
              ListTile(
                leading: const Icon(Icons.add),
                title: const Text('Add Academic Year'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToAddAcademicYear();
                },
              ),
              ListTile(
                leading: const Icon(Icons.calendar_today),
                title: const Text('Manage Academic Year'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToManageAcademicYear();
                },
              ),
            ],
          ),

          // Attendance Management Section
          ExpansionTile(
            leading: const Icon(Icons.assignment_turned_in),
            title: const Text('Attendance'),
            children: [
              ListTile(
                leading: const Icon(Icons.visibility),
                title: const Text('View Attendance'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToViewAttendance();
                },
              ),
              ListTile(
                leading: const Icon(Icons.edit),
                title: const Text('Edit Attendance'),
                contentPadding: const EdgeInsets.only(left: 72, right: 16),
                onTap: () {
                  Navigator.pop(context);
                  _navigateToEditAttendance();
                },
              ),
            ],
          ),

          const Divider(),

          // Settings
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('Settings'),
            onTap: () {
              Navigator.pop(context);
              _navigateToSettings();
            },
          ),

          // Profile
          ListTile(
            leading: const Icon(Icons.person),
            title: const Text('Profile'),
            onTap: () {
              Navigator.pop(context);
              _navigateToProfile();
            },
          ),

          // Logout
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('Logout', style: TextStyle(color: Colors.red)),
            onTap: () {
              Navigator.pop(context);
              _handleLogout();
            },
          ),
        ],
      ),
    );
  }
}
