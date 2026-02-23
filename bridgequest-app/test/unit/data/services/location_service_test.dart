import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geolocator_platform_interface/geolocator_platform_interface.dart';
import 'package:mockito/mockito.dart';

import 'package:bridgequest/data/services/location_service.dart';

import '../../../helpers/mocks.dart';

void main() {
  late MockGeolocatorPlatform mockPlatform;
  late LocationService service;

  setUp(() {
    mockPlatform = MockGeolocatorPlatform();
    GeolocatorPlatform.instance = mockPlatform;
    service = LocationService();
  });

  group('LocationService', () {
    group('ensurePermission', () {
      test('returns serviceDisabled when location service is off', () async {
        when(mockPlatform.isLocationServiceEnabled())
            .thenAnswer((_) async => false);

        final result = await service.ensurePermission();

        expect(result, LocationPermissionResult.serviceDisabled);
      });

      test('returns permissionDenied when already denied', () async {
        when(mockPlatform.isLocationServiceEnabled())
            .thenAnswer((_) async => true);
        when(mockPlatform.checkPermission())
            .thenAnswer((_) async => LocationPermission.denied);
        when(mockPlatform.requestPermission())
            .thenAnswer((_) async => LocationPermission.denied);

        final result = await service.ensurePermission();

        expect(result, LocationPermissionResult.permissionDenied);
      });

      test('returns permissionDenied when deniedForever', () async {
        when(mockPlatform.isLocationServiceEnabled())
            .thenAnswer((_) async => true);
        when(mockPlatform.checkPermission())
            .thenAnswer((_) async => LocationPermission.deniedForever);

        final result = await service.ensurePermission();

        expect(result, LocationPermissionResult.permissionDenied);
        verifyNever(mockPlatform.requestPermission());
      });

      test('returns granted when permission already whileInUse', () async {
        when(mockPlatform.isLocationServiceEnabled())
            .thenAnswer((_) async => true);
        when(mockPlatform.checkPermission())
            .thenAnswer((_) async => LocationPermission.whileInUse);

        final result = await service.ensurePermission();

        expect(result, LocationPermissionResult.granted);
        verifyNever(mockPlatform.requestPermission());
      });

      test('requests permission when denied, then succeeds', () async {
        when(mockPlatform.isLocationServiceEnabled())
            .thenAnswer((_) async => true);
        when(mockPlatform.checkPermission())
            .thenAnswer((_) async => LocationPermission.denied);
        when(mockPlatform.requestPermission())
            .thenAnswer((_) async => LocationPermission.whileInUse);

        final result = await service.ensurePermission();

        expect(result, LocationPermissionResult.granted);
        verify(mockPlatform.requestPermission()).called(1);
      });
    });

    group('startTracking / stopTracking', () {
      test('sets isTracking to true when started', () {
        final controller = StreamController<Position>();
        when(
          mockPlatform.getPositionStream(
            locationSettings: anyNamed('locationSettings'),
          ),
        ).thenAnswer((_) => controller.stream);

        service.startTracking(onPositionChanged: (_, __) {});

        expect(service.isTracking, isTrue);

        service.stopTracking();
        controller.close();
      });

      test('calls onPositionChanged when stream emits', () async {
        final controller = StreamController<Position>();
        when(
          mockPlatform.getPositionStream(
            locationSettings: anyNamed('locationSettings'),
          ),
        ).thenAnswer((_) => controller.stream);

        final positions = <(double, double)>[];
        service.startTracking(
          onPositionChanged: (lat, lng) => positions.add((lat, lng)),
        );

        controller.add(
          Position(
            latitude: 48.8566,
            longitude: 2.3522,
            timestamp: DateTime.now(),
            accuracy: 10,
            altitude: 0,
            altitudeAccuracy: 0,
            heading: 0,
            headingAccuracy: 0,
            speed: 0,
            speedAccuracy: 0,
          ),
        );

        await Future<void>.delayed(Duration.zero);

        expect(positions, hasLength(1));
        expect(positions.first.$1, closeTo(48.8566, 0.0001));
        expect(positions.first.$2, closeTo(2.3522, 0.0001));

        service.stopTracking();
        controller.close();
      });

      test('stopTracking sets isTracking to false', () {
        final controller = StreamController<Position>();
        when(
          mockPlatform.getPositionStream(
            locationSettings: anyNamed('locationSettings'),
          ),
        ).thenAnswer((_) => controller.stream);

        service.startTracking(onPositionChanged: (_, __) {});
        expect(service.isTracking, isTrue);

        service.stopTracking();
        expect(service.isTracking, isFalse);

        controller.close();
      });
    });
  });
}
