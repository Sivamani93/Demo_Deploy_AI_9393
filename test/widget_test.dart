import 'package:flutter_test/flutter_test.dart';
import 'package:ai_mobile_demo/main.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('adds a todo item from input', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());
    expect(find.text('Todo'), findsOneWidget);

    await tester.enterText(find.byKey(const Key('todo_input')), 'Buy milk');
    await tester.tap(find.byKey(const Key('add_button')));
    await tester.pump();

    expect(find.text('Buy milk'), findsOneWidget);
  });

  test('simple math passes', () {
    expect(3 * 3, 9);
  });
}
