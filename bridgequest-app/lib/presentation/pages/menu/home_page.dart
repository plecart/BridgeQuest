import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/exceptions/app_exceptions.dart';
import '../../../data/models/game/game.dart';
import '../../../data/models/user.dart';
import '../../../data/repositories/game_repository.dart';
import '../../../i18n/app_localizations.dart';
import '../../../providers/auth_provider.dart';
import '../../../core/utils/user_helpers.dart';
import '../../pages/lobby/lobby_page.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/user_avatar.dart';

/// Page d'accueil affichant le profil de l'utilisateur et les actions
/// Créer / Rejoindre une partie.
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;

    if (user == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.homeTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _handleLogout(context, authProvider),
            tooltip: l10n.homeLogoutButton,
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              UserAvatar(user: user, radius: 60),
              const SizedBox(height: 24),
              _buildUserName(user),
              const SizedBox(height: 8),
              _buildUserEmail(context, user),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: () => _showCreateGameDialog(context),
                icon: const Icon(Icons.add),
                label: Text(l10n.homeCreateGameButton),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () => _showJoinGameDialog(context),
                icon: const Icon(Icons.login),
                label: Text(l10n.homeJoinGameButton),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _showCreateGameDialog(BuildContext context) async {
    final l10n = AppLocalizations.of(context)!;
    final game = await _showGameInputDialog<Game>(
      context: context,
      title: l10n.homeCreateGameButton,
      label: l10n.homeGameNameLabel,
      submitLabel: l10n.homeCreateGameSubmit,
      submit: (value) => context.read<GameRepository>().createGame(name: value),
      validate: (value) => value.isEmpty ? l10n.errorGeneric : null,
      textCapitalization: TextCapitalization.words,
    );
    if (context.mounted && game != null) {
      _navigateToLobby(context, game);
    }
  }

  Future<void> _showJoinGameDialog(BuildContext context) async {
    final l10n = AppLocalizations.of(context)!;
    final game = await _showGameInputDialog<Game>(
      context: context,
      title: l10n.homeJoinGameButton,
      label: l10n.homeGameCodeLabel,
      submitLabel: l10n.homeJoinGameSubmit,
      submit: (value) => context.read<GameRepository>().joinGame(code: value),
      validate: (value) => value.isEmpty ? l10n.errorGameInvalidCode : null,
      transformInput: (v) => v.toUpperCase(),
      textCapitalization: TextCapitalization.characters,
    );
    if (context.mounted && game != null) {
      _navigateToLobby(context, game);
    }
  }

  void _navigateToLobby(BuildContext context, Game game) {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => LobbyPage(game: game)),
    );
  }

  /// Affiche un dialogue de saisie pour créer ou rejoindre une partie.
  Future<T?> _showGameInputDialog<T>({
    required BuildContext context,
    required String title,
    required String label,
    required String submitLabel,
    required Future<T> Function(String value) submit,
    required String? Function(String value) validate,
    String Function(String value) transformInput = _identity,
    TextCapitalization textCapitalization = TextCapitalization.words,
  }) async {
    return showDialog<T?>(
      context: context,
      builder: (ctx) => _GameInputDialog<T>(
        title: title,
        label: label,
        submitLabel: submitLabel,
        submit: submit,
        validate: validate,
        transformInput: transformInput,
        textCapitalization: textCapitalization,
      ),
    );
  }

  static String _identity(String value) => value;

  /// Construit le nom de l'utilisateur
  Widget _buildUserName(User user) {
    final displayName = UserHelpers.getDisplayName(user);
    return Text(
      displayName,
      style: AppTextStyles.homeTitle,
      textAlign: TextAlign.center,
    );
  }

  /// Construit l'email de l'utilisateur
  Widget _buildUserEmail(BuildContext context, User user) {
    return Text(
      user.email,
      style: AppTextStyles.homeEmail(context),
      textAlign: TextAlign.center,
    );
  }

  /// Gère la déconnexion
  Future<void> _handleLogout(
    BuildContext context,
    AuthProvider authProvider,
  ) async {
    try {
      await authProvider.logout();
    } catch (e) {
      // L'erreur est gérée par le provider
      // La navigation sera gérée par le widget de navigation conditionnelle
    }
  }
}

/// Dialogue de saisie pour créer ou rejoindre une partie.
class _GameInputDialog<T> extends StatefulWidget {
  const _GameInputDialog({
    required this.title,
    required this.label,
    required this.submitLabel,
    required this.submit,
    required this.validate,
    required this.transformInput,
    required this.textCapitalization,
  });

  final String title;
  final String label;
  final String submitLabel;
  final Future<T> Function(String value) submit;
  final String? Function(String value) validate;
  final String Function(String value) transformInput;
  final TextCapitalization textCapitalization;

  @override
  State<_GameInputDialog<T>> createState() => _GameInputDialogState<T>();
}

class _GameInputDialogState<T> extends State<_GameInputDialog<T>> {
  late final TextEditingController _controller;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    final l10n = AppLocalizations.of(context)!;
    final raw = _controller.text.trim();
    final value = widget.transformInput(raw);
    final validationError = widget.validate(value);
    if (validationError != null) {
      setState(() => _errorMessage = validationError);
      return;
    }
    try {
      final result = await widget.submit(value);
      if (mounted) Navigator.of(context).pop(result);
    } on GameException catch (e) {
      setState(
        () => _errorMessage = e.serverMessage ?? l10n.errorGeneric,
      );
    } catch (e) {
      setState(() => _errorMessage = l10n.errorGeneric);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return AlertDialog(
      title: Text(widget.title),
      content: TextField(
        controller: _controller,
        decoration: InputDecoration(
          labelText: widget.label,
          errorText: _errorMessage,
        ),
        textCapitalization: widget.textCapitalization,
        onChanged: (_) => setState(() => _errorMessage = null),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(l10n.commonDialogCancel),
        ),
        FilledButton(
          onPressed: _handleSubmit,
          child: Text(widget.submitLabel),
        ),
      ],
    );
  }
}
