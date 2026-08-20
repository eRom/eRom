# Profil GitHub eRom

`profile.svg` est généré, jamais édité à la main.

## Régénérer

```bash
python3 generate.py
```

## Comment ça marche

- `assets/ascii-art.txt` : le portrait en blocs Unicode (`░▒▓█`), 80 x 43.
- `generate.py` le recadre, le met à l'échelle, et le rend en `<rect>` SVG
  (run-length encodé, 407 rects). Pas de texte pour l'art : l'alignement ne
  dépend d'aucune police installée chez le visiteur.
- Le panneau de droite est du texte mono avec fallback système.
- Palette : design system eRom perso (OKLCH converti en hex), dark-first, brand amber.

## Un seul fichier, pas de dark/light

L'art encode la luminosité : dense = clair. Il suppose un fond sombre. Sur fond
clair il rend un négatif illisible. La carte reste donc sombre dans les deux
thèmes GitHub, comme un terminal.

## Stats

Figées à la main dans le dict `STATS` (generate.py).

### Récupérer les chiffres à jour

Les trois valeurs du bloc STATS en une commande (gh CLI authentifié requis) :

```bash
gh api graphql -f query='{
  viewer {
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection { totalCommitContributions }
    repositoriesContributedTo(includeUserRepositories: true, contributionTypes: [COMMIT]) { totalCount }
  }
}' --jq '.data.viewer | "depots=\(.repositories.totalCount)  commits12m=\(.contributionsCollection.totalCommitContributions)  contribues=\(.repositoriesContributedTo.totalCount)"'
```

`contributionsCollection` sans argument couvre glissant les **12 derniers mois** :
c'est exactement la ligne « Commits (12 mois) ». Reporter les trois valeurs dans
`STATS`, puis `python3 generate.py`.

Le champ `since` (« Membre depuis ») et l'uptime se calculent seuls depuis la
constante `JOINED`, rien à toucher.

### Plus tard, en automatique

Les valeurs dynamiques portent déjà un `id` SVG (`uptime_data`, `repo_data`,
`commit_data`) : une GitHub Action pourra les réécrire sans toucher au reste du
fichier.
