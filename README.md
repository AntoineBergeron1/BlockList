# 420-18D-FX-Maxime-Antoine-Ariane

[![Django CI](https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane/actions/workflows/django.yml/badge.svg)](https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane/actions/workflows/django.yml)

# Co-développeur.euse.s
* Nom étudiant.e 1 : MAXIME MICHAUD
* Nom étudiant.e 2 : ANTOINE BERGERON
* Nom étudiant.e 3 : ARIANE PAQUET

# LIENS IMPORTANTS
* **GitHub :** https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane
* **Trello :** https://trello.com/b/5NpoecUT/projet-web
* **Hébergement :** https://blocklist.mich.sh
* **Documentation :** https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane/wiki
* **Figma :** https://www.figma.com/design/0d10QDbo4IbOutv3pELJT8/Projet-Web?t=8PC1x378Z0OaPn5T-1

# DESCRIPTION
Ce projet consiste en le développement d'une application web transactionnelle complète dans le cadre du cours 420-18D-FX - Projet d'approfondissement Web.

L'application permet [DESCRIPTION DÉTAILLÉE - À COMPLÉTER].

Les objectifs pédagogiques incluent la gestion de projet agile, le développement full-stack, l'implémentation de fonctionnalités AJAX, la sécurisation d'application web et le déploiement en production.

# FONCTIONNALITÉS PRINCIPALES
* **Gestion des utilisateurs :** Inscription, connexion, profils avec authentification sécurisée
* **Transactions :** Vérification d'adresses IP (IPv4/IPv6), soumission de rapports d'abus, consultation d'historique avec système de quotas anti-abus
* **Recherche avancée :** Filtres multiples et tri dynamique
* **Validations AJAX :** Validation en temps réel des formulaires
* **Interface responsive :** Adaptée pour tous les appareils
* **Sécurité :** Gestion des permissions et protection contre les attaques courantes
* **Pages d'erreur personnalisées :** 400, 401, 403, 404, 500

# TECHNOLOGIES UTILISÉES

## Backend
* **Framework :** Django 5.2 (LTS)
* **Langage :** Python 3.13+
* **Base de données :** PostgreSQL
* **ORM :** Django ORM

## Frontend
* **HTML5/CSS3**
* **JavaScript (ES6+)** [À COMPLÉTER]
* **Framework CSS :** Bootstrap 5.x / [À COMPLÉTER]
* **AJAX :** [À COMPLÉTER]

## Outils de développement
* **Gestion de version :** Git/GitHub
* **Gestion de projet :** Trello (Scrum/Agile)
* **IDE recommandé :** VS Code / PyCharm
* **Hébergement :** VPS / Dedicated avec Docker (CD)

# PRÉREQUIS
* Python 3.13 ou supérieur
* pip (gestionnaire de paquets Python)
* Git
* PostgreSQL 17
* Environnement virtuel Python (venv) / anaconda

# INSTALLATION

## 1. Cloner le repository
```bash
git clone https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane.git
cd 420-18D-FX-Maxime-Antoine-Ariane
```

## 2. Créer et activer l'environnement virtuel
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

## 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

## 4. Configurer les variables d'environnement
```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer le fichier .env avec vos configurations
```

## 5. Appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 6. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

## 7. Lancer le serveur de développement
```bash
python manage.py runserver
```

L'application sera accessible à : http://127.0.0.1:8000/

En production après le cd TOUJOURS EN DÉVELOPPEMENT, cela ira sur un sous-domaine.

# STRUCTURE DU PROJET [Exemple]
```
420-18D-FX-Maxime-Antoine-Ariane/
├── projet/                 # Configuration principale Django
│   ├── settings.py        # Paramètres du projet
│   ├── urls.py           # Routes principales
│   └── wsgi.py           # Configuration WSGI
├── apps/                  # Applications Django
│   ├── utilisateurs/     # Gestion des utilisateurs
│   ├── [autres_apps]/    # Autres modules
├── static/               # Fichiers statiques (CSS, JS, images)
├── templates/            # Templates HTML
├── media/                # Fichiers uploadés
├── requirements.txt      # Dépendances Python
├── .env.example         # Exemple de configuration
├── .gitignore           # Fichiers ignorés par Git
└── README.md            # Ce fichier
```

# CONVENTIONS DE CODE

## Python/Django

Nous suivons les conventions Django standards documentées dans le cours 420-15D-FX (Applications Web et sécurité) :
* **Documentation de référence :** https://15d.gitlab.io/docs/django/7-conventions.html

## JavaScript

[À COMPLÉTER]

## Git

### Conventional Commits (Recommandé)

> **Note :** L'utilisation des Conventional Commits est **facultative** mais fortement recommandée pour améliorer la lisibilité et la traçabilité de l'historique Git.

Nous encourageons l'utilisation de la spécification **[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)** pour standardiser nos messages de commit.

**Format de base :** 
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Langue des commits
* **Choisir une langue (anglais OU français) et s'y tenir**
* Idéalement : convention unifiée au niveau du repository
* Au minimum : cohérence personnelle par développeur
* Exemples acceptés :
  * Anglais : `feat(auth): add password recovery`
  * Français : `feat(auth): ajout de la récupération de mot de passe`

### Types principaux
* `feat:` nouvelle fonctionnalité
* `fix:` correction de bug
* `docs:` changements de documentation uniquement
* `style:` formatage, points-virgules manquants, etc. (pas de changement de code)
* `refactor:` refactorisation du code (ni feat, ni fix)
* `perf:` amélioration des performances
* `test:` ajout ou modification de tests
* `chore:` maintenance, mise à jour de dépendances
* `build:` changements du système de build
* `ci:` changements de configuration CI/CD

### Commits complexes
Pour les modifications importantes, utilisez le **corps du message** pour détailler :
```
feat(reports): add comprehensive IP reputation reporting system

- Implemented daily/weekly/monthly report generation
- Added PDF export functionality
- Created email notification system for critical threats
- Integrated with existing dashboard charts
- Added database indices for performance optimization

Closes #45, #47
```

### Exemples de bons commits
```bash
# Simple et clair
fix(api): correct IP validation for IPv6 addresses

# Avec scope précis
feat(dashboard): add real-time threat map visualization

# Breaking change
feat(api)!: change authentication from JWT to OAuth2

BREAKING CHANGE: JWT tokens are no longer supported.
Users must re-authenticate using OAuth2.

# Commit détaillé pour changement complexe
refactor(database): optimize IP lookup performance

Restructured the IP reputation database schema to improve
query performance:
- Added composite index on (ip_address, report_date)
- Denormalized frequently accessed data
- Implemented table partitioning by month

This reduces average query time from 850ms to 45ms for
high-traffic endpoints.
```

### Conseils pratiques
* Un commit = un changement logique
* Écrire au présent impératif : "add feature" et non "added feature"
* La première ligne doit faire max 50-72 caractères
* Référencer les issues/tickets quand pertinent : `fixes #123`
* Pour les petits changements, le titre seul suffit
* Pour les gros changements, toujours ajouter une description détaillée

# SPRINTS
# SPRINTS [À MODIFIER, EXEMPLE, TRELLO PRIORITAIRE]

## Sprint 1 (Semaines 1-6)
* Configuration de l'environnement
* Architecture de base
* Modèles de données
* Authentification

## Sprint 2 (Semaines 7-9)
* Fonctionnalités principales
* Interface utilisateur
* Validations AJAX

## Sprint 3 (Semaines 10-12)
* Fonctionnalités avancées
* Tests et corrections
* Optimisations

## Remise finale (Semaines 13-16)
* Documentation complète
* Déploiement en production
* Présentation

# TESTS [À COMPLÉTER]
```bash
```

# DÉPLOIEMENT
[Instructions de déploiement à compléter selon la plateforme choisie]

Petit VPS ou serveur dédié

Stack équivalente avec NGINX.

Pour le CD, combler avec Docker.

# LICENCE
Ce projet est développé dans le cadre du cours 420-18D-FX au Cégep Garneau.

# CONTACT
* **Professeur :** Nicolas Richard - nrichard@cegepgarneau.ca
* **Équipe de développement :** Via Trello & Teams

# REMERCIEMENTS
* Nicolas Richard - Professeur du cours
* Département d'informatique - Cégep Garneau