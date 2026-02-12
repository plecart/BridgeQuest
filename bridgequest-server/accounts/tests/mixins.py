"""
Mixins de test réutilisables pour le module Accounts.

Fournit des assertions partagées entre plusieurs fichiers de tests
(ex: validation du format JWT, contrat de réponse login).
"""


class JwtAssertionsMixin:
    """Mixin fournissant des assertions JWT réutilisables dans les TestCase."""

    JWT_SEGMENTS_COUNT = 3  # header.payload.signature

    def _assert_jwt_format(self, token):
        """Vérifie qu'un token a le format JWT (3 segments base64 séparés par des points)."""
        parts = token.split(".")
        self.assertEqual(
            len(parts),
            self.JWT_SEGMENTS_COUNT,
            "Un JWT doit contenir header.payload.signature",
        )

    def _assert_login_response_contains_valid_tokens(self, data):
        """Vérifie que la réponse de login contient des tokens JWT access/refresh valides."""
        self.assertIn("access", data, "La réponse doit contenir un token 'access'")
        self.assertIn("refresh", data, "La réponse doit contenir un token 'refresh'")
        self.assertIsInstance(data["access"], str)
        self.assertIsInstance(data["refresh"], str)
        self.assertGreater(
            len(data["access"]), 0, "Le token 'access' ne doit pas être vide"
        )
        self.assertGreater(
            len(data["refresh"]), 0, "Le token 'refresh' ne doit pas être vide"
        )
        self._assert_jwt_format(data["access"])
        self._assert_jwt_format(data["refresh"])
