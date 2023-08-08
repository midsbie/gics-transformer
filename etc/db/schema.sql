-- GICS Sectors
CREATE TABLE gics_sectors (
    id SERIAL PRIMARY KEY,
    code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL
);
CREATE INDEX idx_gics_sectors_code ON gics_sectors(code);

-- GICS Industry Groups
CREATE TABLE gics_industry_groups (
    id SERIAL PRIMARY KEY,
    id_gics_sector INT NOT NULL,
    code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_gics_sector) REFERENCES gics_sectors(id)
);
CREATE INDEX idx_gics_industry_groups_code ON gics_industry_groups(code);

-- GICS Industries
CREATE TABLE gics_industries (
    id SERIAL PRIMARY KEY,
    id_gics_industry_group INT NOT NULL,
    code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_gics_industry_group) REFERENCES gics_industry_groups(id)
);
CREATE INDEX idx_gics_industries_code ON gics_industries(code);

-- GICS Sub-Industries
CREATE TABLE gics_sub_industries (
    id SERIAL PRIMARY KEY,
    id_gics_industry INT NOT NULL,
    code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1024) NOT NULL,
    FOREIGN KEY (id_gics_industry) REFERENCES gics_industries(id)
);
CREATE INDEX idx_gics_sub_industries_code ON gics_sub_industries(code);
