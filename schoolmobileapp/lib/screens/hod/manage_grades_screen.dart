import 'package:flutter/material.dart';

class ManageGradesScreen extends StatelessWidget {
  const ManageGradesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Manage Grades'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(child: Text('Manage Grades Screen - Coming Soon')),
    );
  }
}
