import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class StudentLeaveScreen extends StatefulWidget {
  const StudentLeaveScreen({super.key});

  @override
  State<StudentLeaveScreen> createState() => _StudentLeaveScreenState();
}

class _StudentLeaveScreenState extends State<StudentLeaveScreen> {
  List<dynamic> _studentLeaveRequests = [];
  bool _isLoading = true;
  String _error = '';
  String _selectedFilter = 'all';

  @override
  void initState() {
    super.initState();
    _loadStudentLeaveRequests();
  }

  Future<void> _loadStudentLeaveRequests() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      // Mock data for now - replace with actual API call
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _isLoading = false;
        _studentLeaveRequests = [
          {
            'id': 1,
            'student_name': 'John Doe',
            'student_id': 'STU001',
            'leave_type': 'Sick Leave',
            'from_date': '2024-01-15',
            'to_date': '2024-01-17',
            'reason': 'Fever and flu symptoms',
            'status': 'pending',
            'applied_date': '2024-01-14',
            'total_days': 3,
          },
          {
            'id': 2,
            'student_name': 'Jane Smith',
            'student_id': 'STU002',
            'leave_type': 'Family Emergency',
            'from_date': '2024-01-20',
            'to_date': '2024-01-22',
            'reason': 'Family emergency - need to travel home',
            'status': 'approved',
            'applied_date': '2024-01-18',
            'total_days': 3,
          },
        ];
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Error loading student leave requests: $e';
      });
    }
  }

  List<dynamic> get _filteredRequests {
    if (_selectedFilter == 'all') {
      return _studentLeaveRequests;
    }
    return _studentLeaveRequests
        .where(
          (request) =>
              request['status']?.toLowerCase() == _selectedFilter.toLowerCase(),
        )
        .toList();
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'approved':
        return Colors.green;
      case 'rejected':
        return Colors.red;
      case 'pending':
      default:
        return Colors.orange;
    }
  }

  Future<void> _updateLeaveStatus(
    Map<String, dynamic> request,
    String status,
  ) async {
    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Row(
          children: [
            CircularProgressIndicator(),
            SizedBox(width: 16),
            Text('Updating status...'),
          ],
        ),
      ),
    );

    try {
      // TODO: Implement API call
      await Future.delayed(const Duration(seconds: 1));

      Navigator.pop(context); // Close loading dialog

      setState(() {
        request['status'] = status;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Leave request ${status.toLowerCase()} successfully'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      Navigator.pop(context); // Close loading dialog
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error updating status: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Student Leave Requests'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          PopupMenuButton<String>(
            onSelected: (String value) {
              setState(() {
                _selectedFilter = value;
              });
            },
            itemBuilder: (BuildContext context) => [
              const PopupMenuItem(value: 'all', child: Text('All Requests')),
              const PopupMenuItem(value: 'pending', child: Text('Pending')),
              const PopupMenuItem(value: 'approved', child: Text('Approved')),
              const PopupMenuItem(value: 'rejected', child: Text('Rejected')),
            ],
            icon: const Icon(Icons.filter_list),
          ),
        ],
      ),
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
                    onPressed: _loadStudentLeaveRequests,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : Column(
              children: [
                // Filter chips
                Container(
                  padding: const EdgeInsets.all(8.0),
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        _buildFilterChip('All', 'all'),
                        _buildFilterChip('Pending', 'pending'),
                        _buildFilterChip('Approved', 'approved'),
                        _buildFilterChip('Rejected', 'rejected'),
                      ],
                    ),
                  ),
                ),
                // Requests list
                Expanded(
                  child: RefreshIndicator(
                    onRefresh: _loadStudentLeaveRequests,
                    child: _filteredRequests.isEmpty
                        ? const Center(
                            child: Text('No student leave requests found'),
                          )
                        : ListView.builder(
                            itemCount: _filteredRequests.length,
                            itemBuilder: (context, index) {
                              final request = _filteredRequests[index];
                              return _buildLeaveRequestCard(request);
                            },
                          ),
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildFilterChip(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4.0),
      child: FilterChip(
        label: Text(label),
        selected: _selectedFilter == value,
        onSelected: (bool selected) {
          setState(() {
            _selectedFilter = value;
          });
        },
        selectedColor: Theme.of(context).primaryColor.withOpacity(0.3),
      ),
    );
  }

  Widget _buildLeaveRequestCard(Map<String, dynamic> request) {
    final status = request['status'] ?? 'pending';

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: _getStatusColor(status),
                  child: Text(
                    request['student_name'][0],
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        request['student_name'],
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text('ID: ${request['student_id']}'),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: _getStatusColor(status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _getStatusColor(status)),
                  ),
                  child: Text(
                    status.toUpperCase(),
                    style: TextStyle(
                      color: _getStatusColor(status),
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text('Leave Type: ${request['leave_type']}'),
            Text(
              'Duration: ${request['from_date']} to ${request['to_date']} (${request['total_days']} days)',
            ),
            Text('Reason: ${request['reason']}'),
            if (status.toLowerCase() == 'pending') ...[
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton.icon(
                    onPressed: () => _updateLeaveStatus(request, 'rejected'),
                    icon: const Icon(Icons.close, size: 16),
                    label: const Text('Reject'),
                    style: TextButton.styleFrom(foregroundColor: Colors.red),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: () => _updateLeaveStatus(request, 'approved'),
                    icon: const Icon(Icons.check, size: 16),
                    label: const Text('Approve'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
