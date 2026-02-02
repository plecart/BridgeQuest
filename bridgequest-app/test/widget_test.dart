// Tests de widgets pour Bridge Quest.
//
// Pour interagir avec un widget dans un test, utilisez WidgetTester
// du package flutter_test. Par exemple, vous pouvez envoyer des gestes
// de tap et scroll. Vous pouvez aussi utiliser WidgetTester pour trouver
// des widgets enfants dans l'arbre de widgets, lire du texte, et vérifier
// que les valeurs des propriétés des widgets sont correctes.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'package:bridgequest/main.dart';
import 'package:bridgequest/core/config/app_providers.dart';
import 'package:bridgequest/i18n/app_localizations.dart';

@Tags(['widget'])
void main() {
  setUpAll(() async {
    // Initialiser dotenv pour les tests
    await dotenv.load(fileName: '.env');
  });

  testWidgets('BridgeQuestApp se construit correctement', (WidgetTester tester) async {
    // Act : Construire l'application avec les providers
    await tester.pumpWidget(
      MultiProvider(
        providers: AppProviders.buildProviders(),
        child: const BridgeQuestApp(),
      ),
    );

    // Attendre que les localisations soient chargées
    await tester.pumpAndSettle();

    // Assert : Vérifier que l'application se construit sans erreur
    expect(find.byType(MaterialApp), findsOneWidget);
    
    // Vérifier que le titre de connexion est affiché (via les localisations)
    final l10n = AppLocalizations.of(tester.element(find.byType(MaterialApp)));
    expect(l10n, isNotNull);
    expect(find.text(l10n!.authLoginTitle), findsOneWidget);
  });
}
