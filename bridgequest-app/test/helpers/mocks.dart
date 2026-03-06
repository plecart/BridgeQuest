import 'package:geolocator_platform_interface/geolocator_platform_interface.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';

import 'package:bridgequest/data/services/api_service.dart';

@GenerateMocks([ApiService])
void main() {}

/// Mock compatible avec [PlatformInterface] (exige `extends`, pas `implements`).
///
/// Fournit des valeurs par défaut pour chaque méthode non-nullable
/// afin que `when()` puisse enregistrer les stubs sans crash.
class MockGeolocatorPlatform extends Mock
    with MockPlatformInterfaceMixin
    implements GeolocatorPlatform {
  @override
  Future<bool> isLocationServiceEnabled() => super.noSuchMethod(
        Invocation.method(#isLocationServiceEnabled, []),
        returnValue: Future<bool>.value(false),
      ) as Future<bool>;

  @override
  Future<LocationPermission> checkPermission() => super.noSuchMethod(
        Invocation.method(#checkPermission, []),
        returnValue:
            Future<LocationPermission>.value(LocationPermission.denied),
      ) as Future<LocationPermission>;

  @override
  Future<LocationPermission> requestPermission() => super.noSuchMethod(
        Invocation.method(#requestPermission, []),
        returnValue:
            Future<LocationPermission>.value(LocationPermission.denied),
      ) as Future<LocationPermission>;

  @override
  Stream<Position> getPositionStream({LocationSettings? locationSettings}) =>
      super.noSuchMethod(
        Invocation.method(
          #getPositionStream,
          [],
          {#locationSettings: locationSettings},
        ),
        returnValue: const Stream<Position>.empty(),
      ) as Stream<Position>;
}
