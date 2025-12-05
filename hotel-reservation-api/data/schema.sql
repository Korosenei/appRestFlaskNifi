-- Connexion à la base de données
\c hotel_reservations;

-- Table des clients
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telephone VARCHAR(20),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des chambres
CREATE TABLE IF NOT EXISTS chambres (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(10) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL, -- Simple, Double, Suite
    prix_par_nuit DECIMAL(10, 2) NOT NULL,
    capacite INTEGER NOT NULL,
    disponible BOOLEAN DEFAULT TRUE
);

-- Table des réservations
CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    chambre_id INTEGER REFERENCES chambres(id) ON DELETE CASCADE,
    date_arrivee DATE NOT NULL,
    date_depart DATE NOT NULL,
    nombre_personnes INTEGER NOT NULL,
    prix_total DECIMAL(10, 2),
    statut VARCHAR(20) DEFAULT 'confirmee', -- confirmee, annulee, terminee
    date_reservation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_dates CHECK (date_depart > date_arrivee)
);

-- Table de staging pour NiFi (données brutes avant transformation)
CREATE TABLE IF NOT EXISTS reservations_staging (
    id SERIAL PRIMARY KEY,
    client_nom VARCHAR(100),
    client_prenom VARCHAR(100),
    client_email VARCHAR(150),
    client_telephone VARCHAR(20),
    chambre_numero VARCHAR(10),
    chambre_type VARCHAR(50),
    date_arrivee VARCHAR(20),
    date_depart VARCHAR(20),
    nombre_personnes VARCHAR(10),
    prix_par_nuit VARCHAR(20),
    statut VARCHAR(20),
    date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    traite BOOLEAN DEFAULT FALSE
);

-- Index pour améliorer les performances
CREATE INDEX idx_reservations_client ON reservations(client_id);
CREATE INDEX idx_reservations_chambre ON reservations(chambre_id);
CREATE INDEX idx_reservations_dates ON reservations(date_arrivee, date_depart);
CREATE INDEX idx_staging_traite ON reservations_staging(traite);

-- Données de test pour les chambres
INSERT INTO chambres (numero, type, prix_par_nuit, capacite) VALUES
('101', 'Simple', 75.00, 1),
('102', 'Simple', 75.00, 1),
('201', 'Double', 120.00, 2),
('202', 'Double', 120.00, 2),
('301', 'Suite', 250.00, 4),
('302', 'Suite', 250.00, 4);

-- Données de test pour les clients (assurez-vous que ces insertions sont bien avant celles des réservations)
INSERT INTO clients (nom, prenom, email, telephone) VALUES
('Dupont', 'Jean', 'jean.dupont@email.com', '+33612345678'),
('Martin', 'Marie', 'marie.martin@email.com', '+33698765432'),
('Dubois', 'Pierre', 'pierre.dubois@email.com', '+33687654321');

-- Données de test pour les réservations
-- Assurez-vous que les `client_id` font bien référence aux IDs existants dans la table `clients`
INSERT INTO reservations (client_id, chambre_id, date_arrivee, date_depart, nombre_personnes, prix_total, statut) VALUES
(1, 1, '2025-12-15', '2025-12-20', 1, 375.00, 'confirmee'),
(2, 3, '2025-12-18', '2025-12-22', 2, 480.00, 'confirmee'),
(3, 5, '2025-12-20', '2025-12-25', 3, 1250.00, 'confirmee');
