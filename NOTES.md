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

Les quatre chiffres vivent dans `stats.json`, relu par `generate.py` à chaque
rendu. Les valeurs figées dans le dict `STATS` ne servent que de repli si le
fichier manque.

`.github/workflows/stats.yml` les rafraîchit chaque jour à 6h17 UTC, régénère
`profile.svg` et ne commit que si quelque chose a bougé. L'auteur du commit est
`github-actions[bot]`, jamais toi : sinon la ligne « Commits (12 mois) » se
mettrait à compter ses propres mises à jour.

### Le workflow exige un PAT

Mesuré le 2026-08-20 sur le run 32349597562 : avec le `GITHUB_TOKEN` du runner,
qui n'est scopé qu'à ce dépôt, GitHub répond `repos_total: 59` et `contrib: 50`
au lieu de 131 et 111. Les dépôts privés sont invisibles, et avec eux les dépôts
privés auxquels tu as contribué. Le workflow lit donc `secrets.PROFILE_PAT` et
refuse de tourner sans lui.

Deux filets, parce que ce run-là avait publié les chiffres dégradés sans broncher
(des entiers positifs passent toute validation naïve) :

- le step « Refuser une regression aberrante » annule la publication si une
  valeur chute de plus de 20 % par rapport au `stats.json` déjà commité ;
- `load_stats()` dans `generate.py` refuse toute valeur absente, nulle, négative
  ou non entière, et se replie sur le dict `STATS` si le fichier manque.

Le PAT (`erom-profile-stats`, secret `PROFILE_PAT`, expire le 20 août 2027)
veut un accès *lecture seule* : fine-grained, **All repositories**, et la
permission **Metadata en Read-only ajoutée à la main**. Les deux sont
nécessaires : cocher « All repositories » en laissant le bloc Permissions à
zéro donne un token qui s'authentifie bien en ton nom, remonte `contrib: 111`,
mais ne voit aucun dépôt privé et répond `repos_total: 59` (run 32350776737).
GitHub ne rend Metadata obligatoire que dès qu'une autre permission dépôt est
demandée ; seule, elle doit être ajoutée explicitement. Signature d'un PAT mal
réglé : `repos_total` égal à `repos_publics`.

À la main, sans attendre le cron :

```bash
gh workflow run stats.yml && sleep 20 && gh run list --workflow stats.yml --limit 1
```

En local, la même requête que celle du workflow écrit le fichier directement :

```bash
gh api graphql -f query='
{
  user(login: "eRom") {
    pub: repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    tous: repositories(ownerAffiliations: OWNER) { totalCount }
    contributionsCollection { totalCommitContributions }
    repositoriesContributedTo(includeUserRepositories: true, contributionTypes: [COMMIT]) { totalCount }
  }
}' --jq '.data.user | {
  repos_publics: .pub.totalCount,
  repos_total: .tous.totalCount,
  contrib: .repositoriesContributedTo.totalCount,
  commits_12m: .contributionsCollection.totalCommitContributions
}' > stats.json && python3 generate.py
```

`contributionsCollection` sans argument couvre glissant les **12 derniers mois** :
c'est exactement la ligne « Commits (12 mois) ». `Membre depuis` et l'uptime se
calculent seuls depuis la constante `JOINED`, rien à toucher.

### Pourquoi on régénère au lieu de patcher le SVG

Les valeurs portent un `id` (`uptime_data`, `repo_data`, `contrib_data`,
`commit_data`), mais les remplacer en place casserait l'alignement : les points
de conduite vivent dans un `<tspan>` voisin sans `id`, et leur nombre dérive de
la longueur de la valeur (`fill = COLS - len(key) - len(val) - 4`). Chaque ligne
du panneau fait exactement 55 caractères, c'est ce qui aligne les valeurs à
droite. Or la chaîne d'uptime mesure 23, 24 ou 25 caractères selon la date
(`17 ans, 0 mois, 0 jours` contre `16 ans, 10 mois, 10 jours`) : un patch
ciblé décalerait cette ligne de 8 à 16 px. Régénérer tout le fichier coûte
moins cher que de dupliquer le calcul de layout hors du générateur.
