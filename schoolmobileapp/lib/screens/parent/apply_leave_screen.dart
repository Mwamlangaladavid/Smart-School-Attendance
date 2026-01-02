import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class ApplyLeaveScreen extends StatefulWidget {
  const ApplyLeaveScreen({super.key});

  @override
  State<ApplyLeaveScreen> createState() => _ApplyLeaveScreenState();
}

class _ApplyLeaveScreenState extends State<ApplyLeaveScreen> {
  final _formKey = GlobalKey<FormState>();
  final _leaveDateController = TextEditingController();
  final _leaveMessageController = TextEditingController();

  List<dynamic> _leaveHistory = [];
  bool _isLoading = false;
  bool _isSubmitting = false;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadLeaveHistory();
  }

  Future<void> _loadLeaveHistory() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    // Mock data for now - replace with actual API call
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _isLoading = false;
      _leaveHistory = [
        {
          'id': 1,
          'leave_date': '2024-01-15',
          'leave_message': 'Medical appointment',
          'leave_status': 1, // 0=pending, 1=approved, 2=rejected
          'created_at': '2024-01-10',
        },
        {
          'id': 2,
          'leave_date': '2024-01-20',
          'leave_message': 'Family emergency',
          'leave_status': 0,
          'created_at': '2024-01-18',
        },
      ];
    });
  }

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );

    if (picked != null) {
      setState(() {
        _leaveDateController.text =
            "${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}";
      });
    }
  }

  Future<void> _submitLeaveApplication() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSubmitting = true;
    });

    try {
      // This would be the actual API call to match Django backend
      final result = await ApiService.applyStudentLeave(
        _leaveDateController.text,
        _leaveMessageController.text,
      );

      if (result['success']) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Leave application submitted successfully!'),
            backgroundColor: Colors.green,
          ),
        );

        // Clear form
        _leaveDateController.clear();
        _leaveMessageController.clear();

        // Reload history
        _loadLeaveHistory();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Failed to submit leave application: ${result['error']}',
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
      );
    } finally {
      setState(() {
        _isSubmitting = false;
      });
    }
  }

  String _getStatusText(int status) {
    switch (status) {
      case 0:
        return 'Pending';
      case 1:
        return 'Approved';
      case 2:
        return 'Rejected';
      default:
        return 'Unknown';
    }
  }

  Color _getStatusColor(int status) {
    switch (status) {
      case 0:
        return Colors.orange;
      case 1:
        return Colors.green;
      case 2:
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(int status) {
    switch (status) {
      case 0:
        return Icons.pending;
      case 1:
        return Icons.check_circle;
      case 2:
        return Icons.cancel;
      default:
        return Icons.help;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Apply for Leave'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Leave Application Form
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Apply for Student Leave',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 16),

                      // Leave Date Field
                      TextFormField(
                        controller: _leaveDateController,
                        decoration: const InputDecoration(
                          labelText: 'Leave Date',
                          hintText: 'Select leave date',
                          prefixIcon: Icon(Icons.calendar_today),
                          border: OutlineInputBorder(),
                        ),
                        readOnly: true,
                        onTap: _selectDate,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please select a leave date';
                          }
                          return null;
                        },
                      ),

                      const SizedBox(height: 16),

                      // Leave Message Field
                      TextFormField(
                        controller: _leaveMessageController,
                        decoration: const InputDecoration(
                          labelText: 'Reason for Leave',
                          hintText: 'Enter reason for leave',
                          prefixIcon: Icon(Icons.message),
                          border: OutlineInputBorder(),
                        ),
                        maxLines: 3,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter reason for leave';
                          }
                          return null;
                        },
                      ),

                      const SizedBox(height: 24),

                      // Submit Button
                      SizedBox(
                        width: double.infinity,
                        height: 50,
                        child: ElevatedButton(
                          onPressed: _isSubmitting
                              ? null
                              : _submitLeaveApplication,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Theme.of(
                              context,
                            ).colorScheme.primary,
                            foregroundColor: Colors.white,
                          ),
                          child: _isSubmitting
                              ? const CircularProgressIndicator(
                                  color: Colors.white,
                                )
                              : const Text(
                                  'Submit Leave Application',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Leave History
            Text(
              'Leave History',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),

            if (_isLoading)
              const Center(child: CircularProgressIndicator())
            else if (_error.isNotEmpty)
              Center(
                child: Column(
                  children: [
                    Icon(Icons.error, size: 64, color: Colors.red[300]),
                    const SizedBox(height: 16),
                    Text(_error),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _loadLeaveHistory,
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              )
            else if (_leaveHistory.isEmpty)
              const Center(
                child: Text(
                  'No leave applications found',
                  style: TextStyle(fontSize: 16),
                ),
              )
            else
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _leaveHistory.length,
                itemBuilder: (context, index) {
                  final leave = _leaveHistory[index];
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8.0),
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: _getStatusColor(leave['leave_status']),
                        child: Icon(
                          _getStatusIcon(leave['leave_status']),
                          color: Colors.white,
                          size: 20,
                        ),
                      ),
                      title: Text('Leave Date: ${leave['leave_date']}'),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Reason: ${leave['leave_message']}'),
                          Text('Applied: ${leave['created_at']}'),
                        ],
                      ),
                      trailing: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: _getStatusColor(
                            leave['leave_status'],
                          ).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: _getStatusColor(leave['leave_status']),
                            width: 1,
                          ),
                        ),
                        child: Text(
                          _getStatusText(leave['leave_status']).toUpperCase(),
                          style: TextStyle(
                            color: _getStatusColor(leave['leave_status']),
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      isThreeLine: true,
                    ),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _leaveDateController.dispose();
    _leaveMessageController.dispose();
    super.dispose();
  }
}
