import 'package:flutter/material.dart';

class ManageStreamsScreen extends StatelessWidget {
  const ManageStreamsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Manage Streams'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(child: Text('Manage Streams Screen - Coming Soon')),
    );
  }
}
