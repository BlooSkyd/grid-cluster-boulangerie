-- Création de la table avec les nouvelles colonnes
CREATE TABLE IF NOT EXISTS pains (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    cuisson VARCHAR(50),
    prix DECIMAL(10, 2),
    poids INTEGER
);

-- Peuplage de la base
INSERT INTO pains (nom, cuisson, prix, poids) VALUES
('Baguette Tradition', 'Bien cuite', 1.20, 250),
('Pain de Campagne', 'Dorée', 2.50, 500),
('Baguette Blanche', 'Blanche', 0.90, 250),
('Pain aux Céréales', 'Normale', 3.00, 400),
('Pavé de seigle', 'Bien cuite', 3.50, 600),
('Flûte', 'Dorée', 1.10, 200),
('Miche de pain', 'Normale', 4.50, 1000);