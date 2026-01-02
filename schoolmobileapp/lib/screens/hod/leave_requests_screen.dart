import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class LeaveRequestsScreen extends StatefulWidget {
  const LeaveRequestsScreen({super.key});

  @override
  State<LeaveRequestsScreen> createState() => _LeaveRequestsScreenState();
}

class _LeaveRequestsScreenState extends State<LeaveRequestsScreen> {
  List<dynamic> _leaveRequests = [];
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadLeaveRequests();
  }

  Future<void> _loadLeaveRequests() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    final result = await ApiService.getLeaveRequests();

    setState(() {
      _isLoading = false;
      if (result['success']) {
        _leaveRequests = result['data'] ?? [];
      } else {
        _error = result['error'] ?? 'Failed to load leave requests';
      }
    });
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

  IconData _getStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'approved':
        return Icons.check;
      case 'rejected':
        return Icons.close;
      case 'pending':
      default:
        return Icons.pending;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Leave Requests'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
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
                    onPressed: _loadLeaveRequests,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: _loadLeaveRequests,
              child: ListView.builder(
                itemCount: _leaveRequests.length,
                itemBuilder: (context, index) {
                  final request = _leaveRequests[index];
                  return Card(
                    margin: const EdgeInsets.all(8.0),
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: _getStatusColor(request['status']),
                        child: Icon(
                          _getStatusIcon(request['status']),
                          color: Colors.white,
                        ),
                      ),
                      title: Text(request['staff_name'] ?? 'Unknown Staff'),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Type: ${request['leave_type']}'),
                          Text(
                            'From: ${request['from_date']} To: ${request['to_date']}',
                          ),
                          Text('Reason: ${request['reason']}'),
                          Text('Status: ${request['status']}'),
                        ],
                      ),
                      isThreeLine: true,
                    ),
                  );
                },
              ),
            ),
    );
  }
}
