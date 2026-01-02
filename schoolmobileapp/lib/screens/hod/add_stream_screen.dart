import 'package:flutter/material.dart';

class AddStreamScreen extends StatelessWidget {
  const AddStreamScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Stream'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(child: Text('Add Stream Screen - Coming Soon')),
    );
  }
}
