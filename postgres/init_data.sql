-- Création de la table avec les nouvelles colonnes
-- Use UUID primary key
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS pains (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prix DECIMAL(10, 2)
);


CREATE TABLE IF NOT EXISTS commandes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ref_id INTEGER NOT NULL,
    qte INTEGER NOT NULL
);


-- Peuplage de la base with generated UUIDs
INSERT INTO pains (nom, prix) VALUES
('Baguette Tradition' 1.2),
('Pain de Campagne',  2.5),
('Baguette Blanche', 0.90,),
('Pain aux Céréales', 3.00),
('Pavé de seigle', 3.50),
('Miche de pain', 4.50);

-- Génération d'une vingtaine de commandes exemples (ref_id correspond aux ids de `pains` : 1..6)
INSERT INTO commandes (ref_id, qte) VALUES (1, 3);
INSERT INTO commandes (ref_id, qte) VALUES (2, 1);
INSERT INTO commandes (ref_id, qte) VALUES (3, 5);
INSERT INTO commandes (ref_id, qte) VALUES (4, 2);
INSERT INTO commandes (ref_id, qte) VALUES (5, 1);
INSERT INTO commandes (ref_id, qte) VALUES (6, 4);
INSERT INTO commandes (ref_id, qte) VALUES (2, 2);
INSERT INTO commandes (ref_id, qte) VALUES (1, 1);
INSERT INTO commandes (ref_id, qte) VALUES (2, 3);
INSERT INTO commandes (ref_id, qte) VALUES (3, 2);
INSERT INTO commandes (ref_id, qte) VALUES (4, 6);
INSERT INTO commandes (ref_id, qte) VALUES (5, 2);
INSERT INTO commandes (ref_id, qte) VALUES (6, 1);
INSERT INTO commandes (ref_id, qte) VALUES (2, 5);
INSERT INTO commandes (ref_id, qte) VALUES (1, 4);
INSERT INTO commandes (ref_id, qte) VALUES (2, 2);
INSERT INTO commandes (ref_id, qte) VALUES (3, 3);
INSERT INTO commandes (ref_id, qte) VALUES (5, 4);
INSERT INTO commandes (ref_id, qte) VALUES (4, 1);
INSERT INTO commandes (ref_id, qte) VALUES (6, 2);

