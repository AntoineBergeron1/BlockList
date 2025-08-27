# 420-18D-FX-Maxime-Antoine-Ariane

[![Django CI](https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane/actions/workflows/django.yml/badge.svg)](https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane/actions/workflows/django.yml)

# Co-développeur.euse.s
* Nom étudiant.e 1 : MAXIME MICHAUD
* Nom étudiant.e 2 : ANTOINE BERGERON
* Nom étudiant.e 3 : ARIANE PAQUET

# LIENS IMPORTANTS
* **GitHub :** https://github.com/MaximeMichaud/420-18D-FX-Maxime-Antoine-Ariane
* **Trello :** https://trello.com/b/5NpoecUT/projet-web
* **Hébergement :** [URL de l'application]
* **Documentation :** [Lien vers la documentation]

# DESCRIPTION
Ce projet consiste en le développement d'une application web transactionnelle complète dans le cadre du cours 420-18D-FX - Projet d'approfondissement Web.

L'application permet [DESCRIPTION DÉTAILLÉE - À COMPLÉTER].

Les objectifs pédagogiques incluent la gestion de projet agile, le développement full-stack, l'implémentation de fonctionnalités AJAX, la sécurisation d'application web et le déploiement en production.

# FONCTIONNALITÉS PRINCIPALES
* **Gestion des utilisateurs :** Inscription, connexion, profils avec authentification sécurisée
* **Transactions :** [Type de transactions - achat/réservation/inscription]
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
* **Framework CSS :** Bootstrap 5 / [À COMPLÉTER]
* **AJAX :** [À COMPLÉTER]

## Outils de développement
* **Gestion de version :** Git/GitHub
* **Gestion de projet :** Trello (Scrum/Agile)
* **IDE recommandé :** VS Code / PyCharm
* **Hébergement :** [Plateforme d'hébergement choisie]

# PRÉREQUIS
* Python 3.13 ou supérieur
* pip (gestionnaire de paquets Python)
* Git
* PostgreSQL 17
* Environnement virtuel Python (venv)

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

# STRUCTURE DU PROJET
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

[À COMPLÉTER]

## JavaScript

[À COMPLÉTER]

## Git
[À COMPLÉTER]

# SPRINTS

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

# LICENCE
Ce projet est développé dans le cadre du cours 420-18D-FX au Cégep Garneau.

# CONTACT
* **Professeur :** Nicolas Richard - nrichard@cegepgarneau.ca
* **Équipe de développement :** Via Trello & Teams

# REMERCIEMENTS
* Nicolas Richard - Professeur du cours
* Département d'informatique - Cégep Garneau