-- GICS Sectors
CREATE TABLE sectors (
    id SERIAL PRIMARY KEY,
    code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL
);
CREATE INDEX idx_sectors_code ON sectors(code);

-- GICS Industry Groups
CREATE TABLE industry_groups (
    id SERIAL PRIMARY KEY,
    id_sector INT NOT NULL,
    code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_sector) REFERENCES sectors(id)
);
CREATE INDEX idx_industry_groups_code ON industry_groups(code);

-- GICS Industries
CREATE TABLE industries (
    id SERIAL PRIMARY KEY,
    id_industry_group INT NOT NULL,
    code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_industry_group) REFERENCES industry_groups(id)
);
CREATE INDEX idx_industries_code ON industries(code);

-- GICS Sub-Industries
CREATE TABLE sub_industries (
    id SERIAL PRIMARY KEY,
    id_industry INT NOT NULL,
    code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1024) NOT NULL,
    FOREIGN KEY (id_industry) REFERENCES industries(id)
);
CREATE INDEX idx_sub_industries_code ON sub_industries(code);
