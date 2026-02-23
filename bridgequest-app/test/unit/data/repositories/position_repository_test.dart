import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';

import 'package:bridgequest/core/config/api_config.dart';
import 'package:bridgequest/core/exceptions/app_exceptions.dart';
import 'package:bridgequest/data/models/game/player_position.dart';
import 'package:bridgequest/data/repositories/position_repository.dart';

import '../../../helpers/mocks.mocks.dart';

void main() {
  late MockApiService mockApiService;
  late PositionRepository repository;

  setUp(() {
    mockApiService = MockApiService();
    repository = PositionRepository(apiService: mockApiService);
  });

  group('PositionRepository', () {
    group(
      'sendPosition',
      () {
        test('calls POST with correct path and data', () async {
          when(
            mockApiService.post(
              any,
              data: anyNamed('data'),
            ),
          ).thenAnswer(
            (_) async => Response(
              requestOptions: RequestOptions(),
              statusCode: 201,
            ),
          );

          await repository.sendPosition(
            gameId: 42,
            latitude: 48.8566,
            longitude: 2.3522,
          );

          verify(
            mockApiService.post(
              ApiConfig.locationUpdate,
              data: {
                'game_id': 42,
                'latitude': '48.8566',
                'longitude': '2.3522',
              },
            ),
          ).called(1);
        });

        test(
          'swallows ApiException without rethrowing',
          () async {
            when(
              mockApiService.post(
                any,
                data: anyNamed('data'),
              ),
            ).thenThrow(ApiException('fail', code: 'error.api.unknown'));

            await expectLater(
              repository.sendPosition(
                gameId: 1,
                latitude: 0,
                longitude: 0,
              ),
              completes,
            );
          },
        );

        test(
          'swallows unexpected exceptions without rethrowing',
          () async {
            when(
              mockApiService.post(
                any,
                data: anyNamed('data'),
              ),
            ).thenThrow(Exception('network down'));

            await expectLater(
              repository.sendPosition(
                gameId: 1,
                latitude: 0,
                longitude: 0,
              ),
              completes,
            );
          },
        );
      },
    );

    group('getGamePositions', () {
      test(
        'parses list of positions from API',
        () async {
          when(
            mockApiService.get(
              any,
              queryParameters: anyNamed('queryParameters'),
            ),
          ).thenAnswer(
            (_) async => Response(
              requestOptions: RequestOptions(),
              statusCode: 200,
              data: [
                {
                  'player_id': 1,
                  'user': {'id': 10, 'username': 'Alice'},
                  'latitude': '48.8566',
                  'longitude': '2.3522',
                  'recorded_at': '2026-01-15T10:00:00Z',
                },
                {
                  'player_id': 2,
                  'user': {'id': 20, 'username': 'Bob'},
                  'latitude': '45.7640',
                  'longitude': '4.8357',
                  'recorded_at': '2026-01-15T10:01:00Z',
                },
              ],
            ),
          );

          final positions = await repository.getGamePositions(42);

          expect(positions, hasLength(2));
          expect(positions[0], isA<PlayerPosition>());
          expect(positions[0].playerId, 1);
          expect(positions[0].username, 'Alice');
          expect(positions[1].playerId, 2);
          verify(mockApiService.get(ApiConfig.gamePositions(42))).called(1);
        },
      );

      test('returns empty list when response data is not a list', () async {
        when(
          mockApiService.get(
            any,
            queryParameters: anyNamed('queryParameters'),
          ),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(),
            statusCode: 200,
            data: 'not a list',
          ),
        );

        final positions = await repository.getGamePositions(1);

        expect(positions, isEmpty);
      });

      test(
        'throws GameException on ApiException',
        () async {
          when(
            mockApiService.get(
              any,
              queryParameters: anyNamed('queryParameters'),
            ),
          ).thenThrow(
            ApiException(
              'server error',
              code: 'error.api.generic',
              serverMessage: 'Erreur serveur',
            ),
          );

          expect(
            () => repository.getGamePositions(1),
            throwsA(
              isA<GameException>().having(
                (e) => e.serverMessage,
                'serverMessage',
                'Erreur serveur',
              ),
            ),
          );
        },
      );

      test(
        'throws GameException with generic code on unexpected error',
        () async {
          when(
            mockApiService.get(
              any,
              queryParameters: anyNamed('queryParameters'),
            ),
          ).thenThrow(Exception('unexpected'));

          expect(
            () => repository.getGamePositions(1),
            throwsA(
              isA<GameException>().having(
                (e) => e.code,
                'code',
                'error.generic',
              ),
            ),
          );
        },
      );
    });
  });
}
