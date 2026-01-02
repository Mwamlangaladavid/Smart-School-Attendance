import 'package:flutter/material.dart';

class ParentFeedbackScreen extends StatelessWidget {
  const ParentFeedbackScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Parent Feedback'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(child: Text('Parent Feedback Screen - Coming Soon')),
    );
  }
}
