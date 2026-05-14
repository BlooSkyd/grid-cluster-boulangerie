-- Table d'agrégation sur la slave : compta par pain
CREATE TABLE IF NOT EXISTS compta (
    ref_id INTEGER PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prix_total DECIMAL(18,2) DEFAULT 0,
    nb_cmd INTEGER DEFAULT 0
);

INSERT INTO compta (ref_id, nom, prix_total, nb_cmd) values
(1, 'Baguette Tradition', 45.0, 11),
(2, 'Pain de Campagne', 4.0, 5),
(3, 'Baguette Blanche', 15.0, 15),
(4, 'Pain aux Céréales', 145.0, 20);

-- Vue pour obtenir le top 5 des ventes par prix_total
CREATE OR REPLACE VIEW v_top3_ventes AS
SELECT ref_id, nom, prix_total, nb_cmd
FROM compta
ORDER BY prix_total DESC
LIMIT 3;
