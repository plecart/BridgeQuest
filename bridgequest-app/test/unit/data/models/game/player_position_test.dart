import 'package:flutter_test/flutter_test.dart';

import 'package:bridgequest/data/models/game/player_position.dart';

void main() {
  group('PlayerPosition', () {
    group('fromWebSocketEvent', () {
      test('parses string coordinates to doubles', () {
        final position = PlayerPosition.fromWebSocketEvent(
          playerId: 1,
          userId: 10,
          username: 'Alice',
          latitude: '48.8566',
          longitude: '2.3522',
          recordedAt: '2026-01-15T10:30:00Z',
        );

        expect(position.playerId, 1);
        expect(position.userId, 10);
        expect(position.username, 'Alice');
        expect(position.latitude, closeTo(48.8566, 0.0001));
        expect(position.longitude, closeTo(2.3522, 0.0001));
        expect(position.recordedAt.isUtc, isFalse);
      });

      test('handles negative coordinates', () {
        final position = PlayerPosition.fromWebSocketEvent(
          playerId: 2,
          userId: 20,
          username: 'Bob',
          latitude: '-33.8688',
          longitude: '-151.2093',
          recordedAt: '2026-01-15T10:30:00Z',
        );

        expect(position.latitude, closeTo(-33.8688, 0.0001));
        expect(position.longitude, closeTo(-151.2093, 0.0001));
      });
    });

    group('fromJson', () {
      test('parses API response with nested user object', () {
        final json = {
          'player_id': 5,
          'user': {'id': 50, 'username': 'Charlie'},
          'latitude': '45.7640',
          'longitude': '4.8357',
          'recorded_at': '2026-01-15T12:00:00Z',
        };

        final position = PlayerPosition.fromJson(json);

        expect(position.playerId, 5);
        expect(position.userId, 50);
        expect(position.username, 'Charlie');
        expect(position.latitude, closeTo(45.7640, 0.0001));
        expect(position.longitude, closeTo(4.8357, 0.0001));
      });

      test('handles null user object gracefully', () {
        final json = {
          'player_id': 6,
          'user': null,
          'latitude': '0.0',
          'longitude': '0.0',
          'recorded_at': '2026-01-15T12:00:00Z',
        };

        final position = PlayerPosition.fromJson(json);

        expect(position.userId, 0);
        expect(position.username, '');
      });

      test('handles missing user fields gracefully', () {
        final json = {
          'player_id': 7,
          'user': <String, dynamic>{},
          'latitude': '1.0',
          'longitude': '2.0',
          'recorded_at': '2026-01-15T12:00:00Z',
        };

        final position = PlayerPosition.fromJson(json);

        expect(position.userId, 0);
        expect(position.username, '');
      });
    });

    group('equality', () {
      final now = DateTime(2026);

      test('two positions with same playerId are equal', () {
        final a = PlayerPosition(
          playerId: 1,
          userId: 10,
          username: 'Alice',
          latitude: 48.0,
          longitude: 2.0,
          recordedAt: now,
        );
        final b = PlayerPosition(
          playerId: 1,
          userId: 99,
          username: 'Different',
          latitude: 0.0,
          longitude: 0.0,
          recordedAt: now,
        );

        expect(a, equals(b));
        expect(a.hashCode, equals(b.hashCode));
      });

      test('two positions with different playerId are not equal', () {
        final a = PlayerPosition(
          playerId: 1,
          userId: 10,
          username: 'Alice',
          latitude: 48.0,
          longitude: 2.0,
          recordedAt: now,
        );
        final b = PlayerPosition(
          playerId: 2,
          userId: 10,
          username: 'Alice',
          latitude: 48.0,
          longitude: 2.0,
          recordedAt: now,
        );

        expect(a, isNot(equals(b)));
      });
    });
  });
}
