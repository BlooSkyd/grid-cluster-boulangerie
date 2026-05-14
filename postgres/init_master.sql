-- Création de la table avec les nouvelles colonnes

CREATE TABLE IF NOT EXISTS pains (
    id_pain SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prix DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS commandes (
    id_commandes SERIAL PRIMARY KEY,
    ref_id_pain INTEGER REFERENCES pains(id_pain),
    qte INTEGER NOT NULL
);

-- Peuplage de la table `pains`
INSERT INTO pains (nom, prix) VALUES
('Baguette Tradition', 1.20),
('Pain de Campagne', 2.50),
('Baguette Blanche', 0.90),
('Pain aux Céréales', 3.00),
('Pavé de seigle', 3.50),
('Miche de pain', 4.50),
('Ficelle', 1.00);

-- Génération d'une vingtaine de commandes exemples (ref_id correspond aux ids de `pains` : 1..6)
INSERT INTO commandes (ref_id_pain, qte) VALUES (1, 3);
INSERT INTO commandes (ref_id_pain, qte) VALUES (2, 1);
INSERT INTO commandes (ref_id_pain, qte) VALUES (3, 5);
INSERT INTO commandes (ref_id_pain, qte) VALUES (4, 2);
INSERT INTO commandes (ref_id_pain, qte) VALUES (5, 1);
INSERT INTO commandes (ref_id_pain, qte) VALUES (6, 4);
INSERT INTO commandes (ref_id_pain, qte) VALUES (2, 2);
INSERT INTO commandes (ref_id_pain, qte) VALUES (1, 1);
INSERT INTO commandes (ref_id_pain, qte) VALUES (2, 3);
INSERT INTO commandes (ref_id_pain, qte) VALUES (3, 2);
INSERT INTO commandes (ref_id_pain, qte) VALUES (4, 6);
INSERT INTO commandes (ref_id_pain, qte) VALUES (5, 2);
INSERT INTO commandes (ref_id_pain, qte) VALUES (6, 1);
INSERT INTO commandes (ref_id_pain, qte) VALUES (2, 5);
INSERT INTO commandes (ref_id_pain, qte) VALUES (1, 4);
INSERT INTO commandes (ref_id_pain, qte) VALUES (2, 2);
INSERT INTO commandes (ref_id_pain, qte) VALUES (3, 3);
INSERT INTO commandes (ref_id_pain, qte) VALUES (5, 4);
INSERT INTO commandes (ref_id_pain, qte) VALUES (4, 1);
INSERT INTO commandes (ref_id_pain, qte) VALUES (6, 2);

