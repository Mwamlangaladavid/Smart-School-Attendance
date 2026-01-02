import 'package:flutter/material.dart';

class ManageParentsScreen extends StatelessWidget {
  const ManageParentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Manage Parents'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(child: Text('Manage Parents Screen - Coming Soon')),
    );
  }
}
