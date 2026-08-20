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

Figées à la main dans `STATS` (generate.py). Les valeurs dynamiques portent déjà
un `id` SVG (`uptime_data`, `repo_data`, `commit_data`) : une GitHub Action pourra
les réécrire plus tard sans toucher au reste du fichier.
