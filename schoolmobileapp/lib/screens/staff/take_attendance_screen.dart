import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class TakeAttendanceScreen extends StatefulWidget {
  const TakeAttendanceScreen({super.key});

  @override
  State<TakeAttendanceScreen> createState() => _TakeAttendanceScreenState();
}

class _TakeAttendanceScreenState extends State<TakeAttendanceScreen> {
  List<dynamic> _students = [];
  Map<int, bool> _attendance = {};
  bool _isLoading = true;
  String _error = '';
  DateTime _selectedDate = DateTime.now();
  String _selectedClass = '';
  List<String> _classes = [
    'Class 1',
    'Class 2',
    'Class 3',
  ]; // Replace with real data

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

    try {
      final result = await ApiService.getAllStudents();

      setState(() {
        _isLoading = false;
        if (result['success']) {
          _students = result['data'] ?? [];
          // Initialize attendance map
          for (var student in _students) {
            _attendance[student['id']] = false;
          }
        } else {
          _error = result['error'] ?? 'Failed to load students';
        }
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Error loading students: $e';
      });
    }
  }

  Future<void> _submitAttendance() async {
    if (_selectedClass.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a class'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Row(
          children: [
            CircularProgressIndicator(),
            SizedBox(width: 16),
            Text('Submitting attendance...'),
          ],
        ),
      ),
    );

    try {
      // Prepare attendance data
      List<Map<String, dynamic>> attendanceData = [];
      _attendance.forEach((studentId, isPresent) {
        attendanceData.add({
          'student_id': studentId,
          'is_present': isPresent,
          'date': _selectedDate.toIso8601String().split('T')[0],
          'class': _selectedClass,
        });
      });

      // Submit to API (you'll need to implement this in ApiService)
      // final result = await ApiService.submitAttendance(attendanceData);

      Navigator.pop(context); // Close loading dialog

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Attendance submitted successfully!'),
          backgroundColor: Colors.green,
        ),
      );

      Navigator.pop(context); // Go back to dashboard
    } catch (e) {
      Navigator.pop(context); // Close loading dialog
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error submitting attendance: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Take Attendance'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: _submitAttendance,
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
                    onPressed: _loadStudents,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : Column(
              children: [
                // Date and Class Selection
                Container(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Card(
                              child: ListTile(
                                leading: const Icon(Icons.calendar_today),
                                title: const Text('Date'),
                                subtitle: Text(
                                  '${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}',
                                ),
                                onTap: () async {
                                  final date = await showDatePicker(
                                    context: context,
                                    initialDate: _selectedDate,
                                    firstDate: DateTime.now().subtract(
                                      const Duration(days: 30),
                                    ),
                                    lastDate: DateTime.now(),
                                  );
                                  if (date != null) {
                                    setState(() {
                                      _selectedDate = date;
                                    });
                                  }
                                },
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Card(
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 16.0,
                                ),
                                child: DropdownButton<String>(
                                  isExpanded: true,
                                  hint: const Text('Select Class'),
                                  value: _selectedClass.isEmpty
                                      ? null
                                      : _selectedClass,
                                  items: _classes.map((String value) {
                                    return DropdownMenuItem<String>(
                                      value: value,
                                      child: Text(value),
                                    );
                                  }).toList(),
                                  onChanged: (String? newValue) {
                                    setState(() {
                                      _selectedClass = newValue ?? '';
                                    });
                                  },
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          ElevatedButton.icon(
                            onPressed: () {
                              setState(() {
                                _attendance.updateAll((key, value) => true);
                              });
                            },
                            icon: const Icon(Icons.check_circle),
                            label: const Text('Mark All Present'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                              foregroundColor: Colors.white,
                            ),
                          ),
                          ElevatedButton.icon(
                            onPressed: () {
                              setState(() {
                                _attendance.updateAll((key, value) => false);
                              });
                            },
                            icon: const Icon(Icons.cancel),
                            label: const Text('Mark All Absent'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red,
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const Divider(),
                // Student List
                Expanded(
                  child: ListView.builder(
                    itemCount: _students.length,
                    itemBuilder: (context, index) {
                      final student = _students[index];
                      final studentId = student['id'];
                      final isPresent = _attendance[studentId] ?? false;

                      return Card(
                        margin: const EdgeInsets.symmetric(
                          horizontal: 16.0,
                          vertical: 4.0,
                        ),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: isPresent
                                ? Colors.green
                                : Colors.red,
                            child: Icon(
                              isPresent ? Icons.check : Icons.close,
                              color: Colors.white,
                            ),
                          ),
                          title: Text(
                            '${student['first_name']} ${student['last_name']}',
                          ),
                          subtitle: Text(
                            'ID: ${student['id']} | ${student['course'] ?? 'N/A'}',
                          ),
                          trailing: Switch(
                            value: isPresent,
                            onChanged: (bool value) {
                              setState(() {
                                _attendance[studentId] = value;
                              });
                            },
                            activeColor: Colors.green,
                          ),
                          onTap: () {
                            setState(() {
                              _attendance[studentId] = !isPresent;
                            });
                          },
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _submitAttendance,
        icon: const Icon(Icons.save),
        label: const Text('Submit Attendance'),
        backgroundColor: Colors.blue,
      ),
    );
  }
}
