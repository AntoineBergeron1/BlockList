# 420-18D-FX-Maxime-Antoine-Ariane

[![Django CI](https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane/actions/workflows/build.yml/badge.svg)](https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane/actions/workflows/build.yml)

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

L'application permet de vérifier la réputation d'adresses IP (IPv4/IPv6) et de signaler des activités malveillantes. Les utilisateurs peuvent consulter l'historique des abus, soumettre des rapports sur des IP suspectes et contribuer à une base de données collaborative de blocage d'adresses malveillantes.

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

## Démarrage rapide
```bash
# 1. Cloner le repository
git clone https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane.git
cd 420-18D-FX-Maxime-Antoine-Ariane

# 2. Installer les dépendances (dans un environnement virtuel)
pip install -r src/requirements.txt

# 3. Configurer l'environnement
cp src/.env.example src/.env
# Éditer src/.env avec vos configurations

# 4. Lancer avec Docker (recommandé)
cd deployment
docker-compose up
```

L'application sera accessible à : http://127.0.0.1:8000/

# STRUCTURE DU PROJET [Global] [Exemple]
```
420-18D-FX-Maxime-Antoine-Ariane/
├── src/                   # Code source de l'application
│   ├── config/           # Configuration Django
│   ├── deepweb/          # Application principale
│   ├── apps/             # Modules applicatifs
│   └── static/           # Ressources (CSS, JS, images)
├── deployment/           # Configuration de déploiement
│   ├── docker-compose.yml
│   └── nginx.conf
├── docs/                 # Documentation du projet
├── tests/                # Tests automatisés
└── .github/              # Configuration CI/CD
```

# CONVENTIONS DE CODE

## Python/Django

Nous suivons les conventions Django standards documentées dans le cours 420-15D-FX (Applications Web et sécurité) :
* **Documentation de référence :** https://15d.gitlab.io/docs/django/7-conventions.html

## JavaScript

[À COMPLÉTER]

## Git

Pour les conventions de commit et le workflow Git, consultez notre **[Guide des conventions Git](https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane/wiki/Conventions-Git)** dans le wiki.

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

## Infrastructure
- **Hébergeur :** Vultr VPS
- **Type :** High Frequency (Intel)
- **Localisation :** Toronto
- **IPv4 :** 155.138.139.168
- **Accès :** root / W8+sgd)aHosWz?JF

## Déploiement continu
Le déploiement est automatisé via GitHub Actions (CD) sur push vers la branche `main`.

Pour le déploiement manuel :
```bash
cd /home/deploy/app/deployment
docker-compose up -d
```

# LICENCE
Ce projet est développé dans le cadre du cours 420-18D-FX au Cégep Garneau.

# CONTACT
* **Professeur :** Nicolas Richard - nrichard@cegepgarneau.ca
* **Équipe de développement :** Via Trello & Teams

# REMERCIEMENTS
* Nicolas Richard - Professeur du cours
* Département d'informatique - Cégep Garneau