-- Table d'agrégation sur la slave : compta par pain
CREATE TABLE IF NOT EXISTS compta (
    ref_id INTEGER PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prix_total DECIMAL(18,2) DEFAULT 0,
    nb_cmd INTEGER DEFAULT 0
);

-- Vue pour obtenir le top 5 des ventes par prix_total
CREATE OR REPLACE VIEW v_top5_ventes AS
SELECT ref_id, nom, prix_total, nb_cmd
FROM compta
ORDER BY prix_total DESC
LIMIT 5;
