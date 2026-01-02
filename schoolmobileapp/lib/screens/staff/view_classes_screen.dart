import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class ViewClassesScreen extends StatefulWidget {
  const ViewClassesScreen({super.key});

  @override
  State<ViewClassesScreen> createState() => _ViewClassesScreenState();
}

class _ViewClassesScreenState extends State<ViewClassesScreen> {
  List<dynamic> _classes = [];
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadClasses();
  }

  Future<void> _loadClasses() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      // For now, using mock data since you might not have a classes API yet
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _isLoading = false;
        _classes = [
          {
            'id': 1,
            'name': 'Mathematics - Grade 10',
            'subject': 'Mathematics',
            'grade': 'Grade 10',
            'students_count': 25,
            'schedule': 'Mon, Wed, Fri - 9:00 AM',
            'room': 'Room 101',
          },
          {
            'id': 2,
            'name': 'Mathematics - Grade 11',
            'subject': 'Mathematics',
            'grade': 'Grade 11',
            'students_count': 22,
            'schedule': 'Tue, Thu - 10:00 AM',
            'room': 'Room 102',
          },
          {
            'id': 3,
            'name': 'Mathematics - Grade 12',
            'subject': 'Mathematics',
            'grade': 'Grade 12',
            'students_count': 20,
            'schedule': 'Mon, Wed, Fri - 2:00 PM',
            'room': 'Room 103',
          },
        ];
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Error loading classes: $e';
      });
    }
  }

  void _showClassDetails(Map<String, dynamic> classData) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(classData['name']),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDetailRow('Subject', classData['subject']),
            _buildDetailRow('Grade', classData['grade']),
            _buildDetailRow('Students', '${classData['students_count']}'),
            _buildDetailRow('Schedule', classData['schedule']),
            _buildDetailRow('Room', classData['room']),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Navigate to class management
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Class management coming soon!')),
              );
            },
            child: const Text('Manage'),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Classes'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadClasses),
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
                    onPressed: _loadClasses,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: _loadClasses,
              child: _classes.isEmpty
                  ? const Center(
                      child: Text(
                        'No classes assigned',
                        style: TextStyle(fontSize: 18),
                      ),
                    )
                  : ListView.builder(
                      itemCount: _classes.length,
                      itemBuilder: (context, index) {
                        final classData = _classes[index];
                        return Card(
                          margin: const EdgeInsets.symmetric(
                            horizontal: 16.0,
                            vertical: 8.0,
                          ),
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor: Colors.green,
                              child: Text(
                                classData['grade'].toString().substring(
                                  6,
                                ), // Extract grade number
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            title: Text(
                              classData['name'],
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('${classData['students_count']} students'),
                                Text(classData['schedule']),
                                Text('Room: ${classData['room']}'),
                              ],
                            ),
                            trailing: const Icon(Icons.arrow_forward_ios),
                            isThreeLine: true,
                            onTap: () => _showClassDetails(classData),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
