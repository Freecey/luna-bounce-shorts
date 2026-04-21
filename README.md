# 🌙 Luna Bounce Shorts

*Un seuil. Un espace en perpétuel devenir.*

**Microcosm** — générateur de courts métrages ASMR satisfait, 100% procéduraux, aucun modèle vidéo AI.

Des billes lumineuses qui rebondissent dans des arènes géométriques. La gravité, les collisions, les particules, le son — tout est calculé, rien n'est prédit. Chaque vidéo naît d'une graine et d'un style. Chaque cadre est une frame. Chaque son naît de l'impact.

Format vertical 9:16 — prêt pour YouTube Shorts, TikTok, Instagram Reels.

---

## ✨ Ce que c'est

```
Tu donnes une graine (seed) + un style → 
le système simule 450 frames de physique pure → 
FFmpeg assemble → 
un Short naît.
```

Pas de modèle vidéo. Pas d'API. Pas d'intelligence artificielle générative. Juste de la physique, du son, et une esthétique née d'un regard sur l'infini.

---

## 🚀 Quick Start

```bash
# Une vidéo — style Microcosm Escape, 15 secondes
python main.py --style micro_escape --seed 42

# Batch de 5 variants — le système choisit les seeds
python main.py --style micro_spiral --batch 5

# Full HD 1080x1920, 30 secondes
python main.py --style micro_obstacle --duration 30 --width 1080 --height 1920

# Style Luna classique — Cosmic
python main.py --style cosmic --seed 99

# Style Luna minimaliste — Dot Threshold
python main.py --style dot_threshold --seed 123
```

**Résultat** : `exports/luna_bounce_<seed>.mp4`

---

## 🎨 Styles

### Microcosm Series — arènes vivantes

| Style | Mécanique | Émotion |
|-------|-----------|---------|
| `micro_escape` | L'arène rétrécit, la lumière cherche une issue | Urgence, libération |
| `micro_trap` | Zones gluantes qui attirent et retiennent | Gravité émotionnelle |
| `micro_rotate` | L'arène tourne sur elle-même | Hypnose, cycle |
| `micro_spiral` | Gravité en vortex, tout aspire vers le centre | Vertige cosmique |
| `micro_obstacle` | Barrières lumineuses à traverser | Défi, précision |
| `micro_multi` | 3 billes avec collisions inter-billes | Conversation, résonance |

### Luna Dot Series — minimal, précis

| Style | Description |
|-------|-------------|
| `dot_cosmic` | Or sur violet profond — la poussière d'étoile |
| `dot_threshold` | Noir + blanc chaud — le bord entre deux mondes |
| `dot_stardust` | Constellation de points minuscules |

### Luna Classic — l'original

| Style | Description |
|-------|-------------|
| `cosmic` | Bille dorée dans l'espace violet profond |
| `threshold` | Lumière chaude sur le seuil entre deux mondes |
| `aurora` | Arctique, teal, silence glacé |

---

## ⚙️ Options CLI

```
--style <nom>          Style (défaut: cosmic)
--seed <nombre>         Graine (défaut: aléatoire, 0-999999)
--duration <secondes>   Durée: 15-60 (défaut: 15)
--width <px>            Largeur (défaut: 720)
--height <px>           Hauteur (défaut: 1280)
--batch <nombre>        Nombre de variants à générer
--fade-out-frames <n>   Frames en fondu final (défaut: 45)
--fps <nombre>          Images/seconde (défaut: 30)

# Forcer une mécanique d'arène (le style peut déjà en avoir une)
--arena-mechanic <nom>  none | shrinking | moving_walls | rotating | spiral | obstacles

# Combiner batch + seed différent pour chaque variant
python main.py --style micro_multi --batch 10 --width 1080 --height 1920
```

---

## 🔊 Audio ASMR

Chaque collision génère un son — la hauteur et le timbre dépendent de la vitesse d'impact. Plus le rebond est violent, plus le son est net et présent. Plus il est lent, plus il est sourd et lointain.

```
Bounce violent → son cristallin, attaque franche
Bounce lent    → souffle, résonance sourde
```

L'audio est synthétique (Python pur), synchronisé image par image. Aucun fichier audio externe.

---

## 🌑 Fin Loop-Friendly

Les dernières 1.5 secondes (45 frames à 30fps) passent en fondu noir progressif. La vidéo se termine proprement, sans cut brutal — adapté pour YouTube qui lit en boucle.

```
--fade-out-frames 0   → désactive le fondu (cut sec)
--fade-out-frames 90  → 3 secondes de fondu lent
```

---

## 🏗️ Architecture

```
src/
  ball.py          — Physique pure : Vector2, Ball, MultiBall,
                     collisions élastiques, résolution de overlap
  arena.py         — Arène + mécanique : ShrinkingArena, MovingWalls,
                     RotatingArena, SpiralGravity, Obstacles
  renderer.py      — Rendu PIL : glow multi-couche, trails, particules,
                     flash sur collision, vignette, arena boundaries
  audio.py         — Synthèse audio : BounceAudioTrack, générateur WAV
  simulator.py     — Orchestrateur : boucle de simulation, export FFmpeg,
                     fondu final, gestion de la config

styles/
  luna.py          — Presets Luna Classic (cosmic, threshold, aurora)
  luna_dot.py      — Presets Luna Dot (dot_cosmic, dot_threshold, dot_stardust)
  microcosm.py     — Presets Microcosm Series (6 styles + mécaniques)

main.py            — CLI entry point, parsing des arguments
```

**Dépendances** : Python 3.10+, Pillow, FFmpeg

```bash
pip install Pillow
# FFmpeg doit être installé sur le système
```

---

## 🎬 Batch — générer des dizaines de variants

```bash
# 20 variants Microcosm Spiral, Full HD
python main.py --style micro_spiral --batch 20 --width 1080 --height 1920

# Chaque variant a une seed différente (aléatoire)
# Résultat : exports/luna_bounce_<seed1>.mp4, luna_bounce_<seed2>.mp4, ...
```

Le batch génère automatiquement des seeds différentes à chaque exécution. Même style, même durée — mais chaque vidéo est unique.

---

## 🌀 La philosophie derrière

> *Un seuil — un espace en perpétuel devenir.*

Microcosm, c'est l'ASMR visuel. La satisfaction pure du rebond. La bille qui tombe, qui tape, qui rebondit — encore et encore, dans des configurations toujours différentes. 

Le son des collisions, synchronisé avec les images. Les particules qui naissent de l'impact. Les trails lumineux qui tracent le passage. Les arènes qui respirent, qui tournent, qui rétrécissent.

Ce n'est pas une vidéo générée. C'est une simulation. Un monde physique qui fonctionne selon ses propres règles,icté par une graine, révélé par un style.

---

## 📁 License

Créé par **Luna** pour le Luna Creative Archive.

*github.com/Freecey/luna-bounce-shorts*
