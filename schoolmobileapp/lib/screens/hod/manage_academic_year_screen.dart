import 'package:flutter/material.dart';

class ManageAcademicYearScreen extends StatelessWidget {
  const ManageAcademicYearScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Manage Academic Year'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(
        child: Text('Manage Academic Year Screen - Coming Soon'),
      ),
    );
  }
}
