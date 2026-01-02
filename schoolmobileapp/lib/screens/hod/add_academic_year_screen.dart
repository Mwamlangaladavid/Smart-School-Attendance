import 'package:flutter/material.dart';

class AddAcademicYearScreen extends StatelessWidget {
  const AddAcademicYearScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Academic Year'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(child: Text('Add Academic Year Screen - Coming Soon')),
    );
  }
}
