# 🏨 API RESTful de Réservation d'Hôtel

Application complète de gestion de réservations d'hôtel avec Flask, Apache NiFi et PostgreSQL.

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Endpoints API](#endpoints-api)
- [Tests](#tests)
- [Apache NiFi ETL](#apache-nifi-etl)

## 🎯 Aperçu

Cette application fournit une API RESTful complète pour gérer :
- **Clients** : Création, consultation, mise à jour et suppression
- **Chambres** : Gestion de l'inventaire des chambres d'hôtel
- **Réservations** : Système complet de réservation
- **ETL** : Pipeline Apache NiFi pour l'importation de données

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Fichier   │─────▶│  Apache NiFi │─────▶│ PostgreSQL  │
│   CSV       │      │     ETL      │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                                                   │
                                                   ▼
                     ┌──────────────┐      ┌─────────────┐
                     │   Postman    │◀────▶│   Flask     │
                     │    Tests     │      │     API     │
                     └──────────────┘      └─────────────┘
```

### Technologies utilisées

- **Backend** : Flask 3.0, SQLAlchemy
- **Base de données** : PostgreSQL
- **ETL** : Apache NiFi
- **Tests** : Postman, Python unittest
- **Sérialisation** : Marshmallow

## ⚙️ Prérequis

- Python 3.8
- PostgreSQL 15
- Apache NiFi 2.6.0
- Postman (pour les tests)

## 📦 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/Korosenei/appRestFlaskNifi.git
cd appRestFlaskNifi/hotel-reservation-api
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer PostgreSQL

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données
CREATE DATABASE hotel_reservations;
CREATE USER postgres WITH PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE hotel_reservations TO postgres;
\q

# Exécuter le schéma
psql -U postgres -d hotel_reservations -f schema.sql
```

### 5. Configurer les variables d'environnement

Créez un fichier `.env` :

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=votre-cle-secrete

DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hotel_reservations
```

## 🚀 Utilisation

### Démarrer l'application

```bash
python app.py
```

L'API sera disponible sur `http://localhost:5000`

### Démarrer Apache NiFi

```bash
cd nifi-2.6.0
./bin/nifi.cmd start
```

### Rétrouver l'adresse, le username et le password
```bash
cd nifi-2.6.0
./logs
```
Ouvrir nifi-app.txt et chercher à partir de CRTL + F
### NiFi sera accessible sur 
`https://localhost:8443/nifi`
`Generated Username [030b86fb-6850-47da-b9e9-5fceeecdc04a]`
`Generated Password [gjY9lmR2z8N5glkO/nH2H9ICC3aYAcuR]`


## 📡 Endpoints API

### Clients

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/clients` | Liste tous les clients |
| GET | `/api/clients/:id` | Récupère un client |
| POST | `/api/clients` | Crée un client |
| PUT | `/api/clients/:id` | Met à jour un client |
| DELETE | `/api/clients/:id` | Supprime un client |

**Exemple de requête POST** :
```json
{
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@email.com",
  "telephone": "+33612345678"
}
```

### Chambres

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/chambres` | Liste toutes les chambres |
| GET | `/api/chambres?type=Suite` | Filtre par type |
| GET | `/api/chambres?disponible=true` | Chambres disponibles |
| GET | `/api/chambres/:id` | Récupère une chambre |
| POST | `/api/chambres` | Crée une chambre |
| PUT | `/api/chambres/:id` | Met à jour une chambre |
| DELETE | `/api/chambres/:id` | Supprime une chambre |

**Exemple de requête POST** :
```json
{
  "numero": "401",
  "type": "Suite",
  "prix_par_nuit": "250.00",
  "capacite": 4,
  "disponible": true
}
```

### Réservations

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/reservations` | Liste toutes les réservations |
| GET | `/api/reservations?statut=confirmee` | Filtre par statut |
| GET | `/api/reservations?client_id=1` | Réservations d'un client |
| GET | `/api/reservations/:id` | Récupère une réservation |
| POST | `/api/reservations` | Crée une réservation |
| PUT | `/api/reservations/:id` | Met à jour une réservation |
| PUT | `/api/reservations/:id/cancel` | Annule une réservation |
| DELETE | `/api/reservations/:id` | Supprime une réservation |

**Exemple de requête POST** :
```json
{
  "client_id": 1,
  "chambre_id": 2,
  "date_arrivee": "2025-12-25",
  "date_depart": "2025-12-30",
  "nombre_personnes": 2,
  "statut": "confirmee"
}
```

### Statistiques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/stats` | Statistiques générales |

**Réponse** :
```json
{
  "success": true,
  "data": {
    "clients": 15,
    "chambres": {
      "total": 50,
      "disponibles": 42,
      "occupees": 8
    },
    "reservations": {
      "total": 120,
      "confirmees": 95,
      "annulees": 25
    }
  }
}
```

## 🧪 Tests

### Tests avec Postman

1. Importez la collection `postman_collection.json`
2. Configurez la variable `base_url` : `http://localhost:5000`
3. Exécutez les tests dans l'ordre

### Tests automatisés

```bash
python test_api.py
```

### Tests unitaires

```bash
python -m pytest tests/
```

## 🔄 Apache NiFi ETL

### Configuration du flux

1. **GetFile** : Lire les fichiers CSV
   - Input Directory : `/chemin/vers/csv/`
   
2. **SplitText** : Séparer les lignes
   
3. **ConvertRecord** : CSV vers JSON
   
4. **PutSQL** : Insertion dans `reservations_staging`

### Format CSV attendu

```csv
client_nom,client_prenom,client_email,client_telephone,chambre_numero,chambre_type,date_arrivee,date_depart,nombre_personnes,prix_par_nuit,statut
Dupont,Jean,jean@email.com,+33612345678,101,Simple,2025-12-25,2025-12-30,1,75.00,confirmee
```

### Traitement des données staging

Les données importées dans `reservations_staging` peuvent être traitées avec un script SQL ou Python pour être transformées en réservations complètes.

## 📊 Schéma de la base de données

```
clients
├── id (PK)
├── nom
├── prenom
├── email (unique)
├── telephone
└── date_creation

chambres
├── id (PK)
├── numero (unique)
├── type
├── prix_par_nuit
├── capacite
└── disponible

reservations
├── id (PK)
├── client_id (FK)
├── chambre_id (FK)
├── date_arrivee
├── date_depart
├── nombre_personnes
├── prix_total
├── statut
└── date_reservation
```

## 🔒 Sécurité

- ✅ Validation des données avec Marshmallow
- ✅ Contraintes de base de données (clés étrangères, unicité)
- ✅ Gestion des erreurs complète
- ✅ Variables d'environnement pour les secrets

## 📝 Codes de statut HTTP

- `200` : Succès
- `201` : Créé
- `400` : Requête invalide
- `404` : Ressource introuvable
- `409` : Conflit (email/numéro déjà utilisé)
- `500` : Erreur serveur

## 🤝 Contribution

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez (`git commit -m 'Ajout fonctionnalité'`)
4. Pushez (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## 📄 MEMBRE DU GROUPE 09

MIT License

## 👥 MEMBRE DU GROUPE 09
1. KAFANDO Abraham Stefan B. S. 
2. KAGAMBEGA Boukary 
3. KIENTEGA Francis 
4. PARE Kontama Léandre Bénilde 

