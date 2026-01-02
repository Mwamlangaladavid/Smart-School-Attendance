import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class ViewAttendanceScreen extends StatefulWidget {
  const ViewAttendanceScreen({super.key});

  @override
  State<ViewAttendanceScreen> createState() => _ViewAttendanceScreenState();
}

class _ViewAttendanceScreenState extends State<ViewAttendanceScreen> {
  Map<String, dynamic>? _attendanceData;
  List<dynamic> _attendanceRecords = [];
  bool _isLoading = true;
  String _error = '';
  String _selectedFilter = 'all'; // all, present, absent
  String _selectedPeriod =
      'current_year'; // current_year, last_30_days, all_time

  @override
  void initState() {
    super.initState();
    _loadAttendanceData();
  }

  Future<void> _loadAttendanceData() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      final result = await ApiService.getParentAttendanceData(_selectedPeriod);

      setState(() {
        _isLoading = false;
        if (result['success']) {
          _attendanceData = result['data']['summary'];
          _attendanceRecords = result['data']['records'] ?? [];
        } else {
          _error = result['error'] ?? 'Failed to load attendance data';
        }
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Error loading attendance: $e';
      });
    }
  }

  List<dynamic> get _filteredRecords {
    if (_selectedFilter == 'all') {
      return _attendanceRecords;
    }
    return _attendanceRecords.where((record) {
      if (_selectedFilter == 'present') {
        return record['status'] == true || record['status'] == 'present';
      } else {
        return record['status'] == false || record['status'] == 'absent';
      }
    }).toList();
  }

  Widget _buildSummaryCard() {
    if (_attendanceData == null) return const SizedBox.shrink();

    final percentage = _attendanceData!['percentage'] ?? 0.0;
    final totalDays = _attendanceData!['total_days'] ?? 0;
    final presentDays = _attendanceData!['present_days'] ?? 0;
    final absentDays = _attendanceData!['absent_days'] ?? 0;

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Attendance Summary',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),

            // Attendance Percentage Circle
            Center(
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 120,
                    height: 120,
                    child: CircularProgressIndicator(
                      value: percentage / 100,
                      strokeWidth: 8,
                      backgroundColor: Colors.grey[300],
                      valueColor: AlwaysStoppedAnimation<Color>(
                        percentage >= 75
                            ? Colors.green
                            : percentage >= 50
                            ? Colors.orange
                            : Colors.red,
                      ),
                    ),
                  ),
                  Column(
                    children: [
                      Text(
                        '${percentage.toStringAsFixed(1)}%',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Text('Attendance', style: TextStyle(fontSize: 12)),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Statistics Row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatColumn(
                  'Total Days',
                  totalDays.toString(),
                  Colors.blue,
                ),
                _buildStatColumn(
                  'Present',
                  presentDays.toString(),
                  Colors.green,
                ),
                _buildStatColumn('Absent', absentDays.toString(), Colors.red),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatColumn(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildFilterChips() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Period Filter
          Text('Period:', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildPeriodChip('Current Year', 'current_year'),
                _buildPeriodChip('Last 30 Days', 'last_30_days'),
                _buildPeriodChip('All Time', 'all_time'),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Status Filter
          Text('Filter:', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildStatusChip('All', 'all'),
                _buildStatusChip('Present', 'present'),
                _buildStatusChip('Absent', 'absent'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPeriodChip(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
      child: FilterChip(
        label: Text(label),
        selected: _selectedPeriod == value,
        onSelected: (bool selected) {
          if (selected) {
            setState(() {
              _selectedPeriod = value;
            });
            _loadAttendanceData();
          }
        },
        selectedColor: Theme.of(context).primaryColor.withOpacity(0.3),
      ),
    );
  }

  Widget _buildStatusChip(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
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

  Widget _buildAttendanceRecord(Map<String, dynamic> record) {
    final date = record['date'] ?? 'N/A';
    final status = record['status'];
    final isPresent = status == true || status == 'present';
    final subject = record['subject'] ?? 'General';
    final remarks = record['remarks'] ?? '';

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: isPresent ? Colors.green : Colors.red,
          child: Icon(
            isPresent ? Icons.check : Icons.close,
            color: Colors.white,
          ),
        ),
        title: Text(date),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Subject: $subject'),
            if (remarks.isNotEmpty) Text('Remarks: $remarks'),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: isPresent
                ? Colors.green.withOpacity(0.1)
                : Colors.red.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isPresent ? Colors.green : Colors.red,
              width: 1,
            ),
          ),
          child: Text(
            isPresent ? 'PRESENT' : 'ABSENT',
            style: TextStyle(
              color: isPresent ? Colors.green : Colors.red,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('View Attendance'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAttendanceData,
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
                  Text(
                    _error,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 16),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loadAttendanceData,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: _loadAttendanceData,
              child: Column(
                children: [
                  // Summary Card
                  _buildSummaryCard(),

                  // Filter Chips
                  _buildFilterChips(),

                  const Divider(),

                  // Records List
                  Expanded(
                    child: _filteredRecords.isEmpty
                        ? const Center(
                            child: Text(
                              'No attendance records found',
                              style: TextStyle(fontSize: 16),
                            ),
                          )
                        : ListView.builder(
                            itemCount: _filteredRecords.length,
                            itemBuilder: (context, index) {
                              return _buildAttendanceRecord(
                                _filteredRecords[index],
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
    );
  }
}
