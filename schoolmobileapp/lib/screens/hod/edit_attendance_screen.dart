import 'package:flutter/material.dart';

class EditAttendanceScreen extends StatelessWidget {
  const EditAttendanceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Attendance'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(child: Text('Edit Attendance Screen - Coming Soon')),
    );
  }
}
