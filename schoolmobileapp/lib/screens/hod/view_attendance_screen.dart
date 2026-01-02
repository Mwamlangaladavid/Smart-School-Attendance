import 'package:flutter/material.dart';

class ViewAttendanceScreen extends StatefulWidget {
  const ViewAttendanceScreen({super.key});

  @override
  State<ViewAttendanceScreen> createState() => _ViewAttendanceScreenState();
}

class _ViewAttendanceScreenState extends State<ViewAttendanceScreen> {
  DateTime _selectedDate = DateTime.now();
  String _selectedGrade = '';
  List<Map<String, dynamic>> _attendanceData = [];
  bool _isLoading = false;

  final List<String> _grades = [
    'Grade 1',
    'Grade 2',
    'Grade 3',
    'Grade 4',
    'Grade 5',
  ];

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now(),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
      });
      _loadAttendanceData();
    }
  }

  Future<void> _loadAttendanceData() async {
    if (_selectedGrade.isEmpty) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // Mock data - replace with actual API call
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _attendanceData = [
          {
            'student_name': 'John Doe',
            'student_id': 'STU001',
            'status': 'Present',
          },
          {
            'student_name': 'Jane Smith',
            'student_id': 'STU002',
            'status': 'Absent',
          },
          {
            'student_name': 'Bob Johnson',
            'student_id': 'STU003',
            'status': 'Present',
          },
        ];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('View Attendance'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: InkWell(
                            onTap: _selectDate,
                            child: InputDecorator(
                              decoration: const InputDecoration(
                                labelText: 'Select Date',
                                prefixIcon: Icon(Icons.calendar_today),
                                border: OutlineInputBorder(),
                              ),
                              child: Text(
                                '${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}',
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            value: _selectedGrade.isEmpty
                                ? null
                                : _selectedGrade,
                            decoration: const InputDecoration(
                              labelText: 'Select Grade',
                              prefixIcon: Icon(Icons.grade),
                              border: OutlineInputBorder(),
                            ),
                            hint: const Text('Choose Grade'),
                            items: _grades.map((String grade) {
                              return DropdownMenuItem<String>(
                                value: grade,
                                child: Text(grade),
                              );
                            }).toList(),
                            onChanged: (String? newValue) {
                              setState(() {
                                _selectedGrade = newValue ?? '';
                              });
                              _loadAttendanceData();
                            },
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _attendanceData.isEmpty
                  ? const Center(
                      child: Text(
                        'Select date and grade to view attendance',
                        style: TextStyle(fontSize: 16),
                      ),
                    )
                  : Card(
                      child: Column(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(16.0),
                            decoration: BoxDecoration(
                              color: Theme.of(
                                context,
                              ).primaryColor.withOpacity(0.1),
                              borderRadius: const BorderRadius.only(
                                topLeft: Radius.circular(8),
                                topRight: Radius.circular(8),
                              ),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.assignment,
                                  color: Theme.of(context).primaryColor,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Attendance for $_selectedGrade',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Theme.of(context).primaryColor,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Expanded(
                            child: ListView.builder(
                              itemCount: _attendanceData.length,
                              itemBuilder: (context, index) {
                                final student = _attendanceData[index];
                                final isPresent =
                                    student['status'] == 'Present';

                                return ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: isPresent
                                        ? Colors.green
                                        : Colors.red,
                                    child: Icon(
                                      isPresent ? Icons.check : Icons.close,
                                      color: Colors.white,
                                    ),
                                  ),
                                  title: Text(student['student_name']),
                                  subtitle: Text(
                                    'ID: ${student['student_id']}',
                                  ),
                                  trailing: Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: isPresent
                                          ? Colors.green.withOpacity(0.1)
                                          : Colors.red.withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(12),
                                      border: Border.all(
                                        color: isPresent
                                            ? Colors.green
                                            : Colors.red,
                                      ),
                                    ),
                                    child: Text(
                                      student['status'],
                                      style: TextStyle(
                                        color: isPresent
                                            ? Colors.green
                                            : Colors.red,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                        ],
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
