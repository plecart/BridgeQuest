import 'package:flutter/material.dart';

import '../../../data/models/game/game_score_entry.dart';
import '../../../i18n/app_localizations.dart';
import '../menu/home_page.dart';

/// Page des résultats affichée après la fin d'une partie.
///
/// Affiche le classement final (scores triés par ordre décroissant),
/// le rôle de chaque joueur, et un bouton pour revenir au menu.
/// Pas de ViewModel nécessaire : la page est purement déclarative.
class ResultsPage extends StatelessWidget {
  const ResultsPage({
    super.key,
    required this.gameId,
    required this.scores,
  });

  final int gameId;
  final List<GameScoreEntry> scores;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return PopScope(
      canPop: false,
      child: Scaffold(
        appBar: AppBar(
          title: Text(l10n.resultsTitle),
          automaticallyImplyLeading: false,
        ),
        body: SafeArea(
          child: scores.isEmpty
              ? _buildEmptyState(context, l10n)
              : _buildScoreboard(context, l10n),
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // État vide
  // ---------------------------------------------------------------------------

  Widget _buildEmptyState(BuildContext context, AppLocalizations l10n) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.emoji_events_outlined, size: 64),
          const SizedBox(height: 16),
          Text(l10n.resultsNoScores),
          const SizedBox(height: 32),
          _buildBackToMenuButton(context, l10n),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Scoreboard
  // ---------------------------------------------------------------------------

  Widget _buildScoreboard(BuildContext context, AppLocalizations l10n) {
    return Column(
      children: [
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildSubtitle(context, l10n),
                const SizedBox(height: 24),
                _buildPodium(context, l10n),
                const SizedBox(height: 24),
                _buildFullRanking(context, l10n),
              ],
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(24),
          child: _buildBackToMenuButton(context, l10n),
        ),
      ],
    );
  }

  Widget _buildSubtitle(BuildContext context, AppLocalizations l10n) {
    return Text(
      l10n.resultsSubtitle,
      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
      textAlign: TextAlign.center,
    );
  }

  // ---------------------------------------------------------------------------
  // Podium (top 3)
  // ---------------------------------------------------------------------------

  Widget _buildPodium(BuildContext context, AppLocalizations l10n) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Icon(Icons.emoji_events, size: 48, color: Colors.amber),
            const SizedBox(height: 12),
            for (var i = 0; i < scores.length && i < 3; i++)
              _buildPodiumEntry(context, scores[i], i + 1, l10n),
          ],
        ),
      ),
    );
  }

  Widget _buildPodiumEntry(
    BuildContext context,
    GameScoreEntry entry,
    int rank,
    AppLocalizations l10n,
  ) {
    final color = _rankColor(rank);
    final icon = _rankIcon(rank);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _displayName(entry, l10n),
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                Text(
                  _localizedRoleName(entry, l10n),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: entry.isSpirit
                            ? Theme.of(context).colorScheme.error
                            : Theme.of(context).colorScheme.primary,
                      ),
                ),
              ],
            ),
          ),
          Text(
            l10n.resultsScorePoints(entry.score),
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Classement complet (à partir du 4e)
  // ---------------------------------------------------------------------------

  Widget _buildFullRanking(BuildContext context, AppLocalizations l10n) {
    if (scores.length <= 3) return const SizedBox.shrink();

    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: scores.length - 3,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final rank = index + 4;
        final entry = scores[index + 3];
        return _buildRankingTile(context, entry, rank, l10n);
      },
    );
  }

  Widget _buildRankingTile(
    BuildContext context,
    GameScoreEntry entry,
    int rank,
    AppLocalizations l10n,
  ) {
    return ListTile(
      leading: CircleAvatar(
        radius: 16,
        backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
        child: Text(
          '$rank',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
      ),
      title: Text(_displayName(entry, l10n)),
      subtitle: Text(_localizedRoleName(entry, l10n)),
      trailing: Text(
        l10n.resultsScorePoints(entry.score),
        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              fontWeight: FontWeight.bold,
            ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Bouton retour au menu
  // ---------------------------------------------------------------------------

  Widget _buildBackToMenuButton(BuildContext context, AppLocalizations l10n) {
    return SizedBox(
      width: double.infinity,
      child: FilledButton.icon(
        onPressed: () => _navigateToMenu(context),
        icon: const Icon(Icons.home),
        label: Text(l10n.resultsBackToMenu),
      ),
    );
  }

  void _navigateToMenu(BuildContext context) {
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const HomePage()),
      (route) => false,
    );
  }

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  /// Nom d'affichage du joueur (fallback si username vide).
  String _displayName(GameScoreEntry entry, AppLocalizations l10n) {
    return entry.username.isNotEmpty
        ? entry.username
        : l10n.lobbyPlayerFallbackName(entry.playerId);
  }

  /// Nom localisé du rôle.
  String _localizedRoleName(GameScoreEntry entry, AppLocalizations l10n) {
    return entry.isSpirit ? l10n.gameRoleSpirit : l10n.gameRoleHuman;
  }

  /// Couleur associée au rang (podium).
  Color _rankColor(int rank) {
    switch (rank) {
      case 1:
        return Colors.amber;
      case 2:
        return Colors.grey;
      case 3:
        return Colors.brown;
      default:
        return Colors.black54;
    }
  }

  /// Icône associée au rang (podium).
  IconData _rankIcon(int rank) {
    switch (rank) {
      case 1:
        return Icons.looks_one;
      case 2:
        return Icons.looks_two;
      case 3:
        return Icons.looks_3;
      default:
        return Icons.circle_outlined;
    }
  }
}
