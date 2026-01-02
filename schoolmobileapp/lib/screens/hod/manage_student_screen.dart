import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class ManageStudentsScreen extends StatefulWidget {
  const ManageStudentsScreen({super.key});

  @override
  State<ManageStudentsScreen> createState() => _ManageStudentsScreenState();
}

class _ManageStudentsScreenState extends State<ManageStudentsScreen> {
  List<dynamic> _studentsList = [];
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadStudents();
  }

  Future<void> _loadStudents() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    final result = await ApiService.getAllStudents();

    setState(() {
      _isLoading = false;
      if (result['success']) {
        _studentsList = result['data'] ?? [];
      } else {
        _error = result['error'] ?? 'Failed to load students';
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Manage Students'),
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
                    onPressed: _loadStudents,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: _loadStudents,
              child: ListView.builder(
                itemCount: _studentsList.length,
                itemBuilder: (context, index) {
                  final student = _studentsList[index];
                  return Card(
                    margin: const EdgeInsets.all(8.0),
                    child: ListTile(
                      leading: CircleAvatar(
                        child: Text(
                          '${student['first_name']?[0] ?? ''}${student['last_name']?[0] ?? ''}',
                        ),
                      ),
                      title: Text(
                        '${student['first_name']} ${student['last_name']}',
                      ),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Email: ${student['email']}'),
                          Text('Course: ${student['course'] ?? 'N/A'}'),
                          if (student['date_joined'] != null)
                            Text('Joined: ${student['date_joined']}'),
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
