import 'package:flutter/material.dart';

void main() {
  print('AI Gate test run'); // <-- new line added
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI-Powered Pipeline Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      home: const TodoPage(),
    );
  }
}

class TodoPage extends StatefulWidget {
  const TodoPage({super.key});
  @override
  State<TodoPage> createState() => _TodoPageState();
}

class _TodoPageState extends State<TodoPage> {
  final controller = TextEditingController();
  final todos = <String>[];

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  void addTodo() {
    final text = controller.text.trim();
    if (text.isNotEmpty) {
      setState(() => todos.add(text));
      controller.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Todo')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              key: const Key('todo_input'),
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'Add todo',
                border: OutlineInputBorder(),
              ),
              onSubmitted: (_) => addTodo(),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              key: const Key('add_button'),
              onPressed: addTodo,
              child: const Text('Add'),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                itemCount: todos.length,
                itemBuilder: (_, i) => ListTile(
                  leading: const Icon(Icons.check_circle_outline),
                  title: Text(todos[i]),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
