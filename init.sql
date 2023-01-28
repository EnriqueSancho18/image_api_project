
CREATE DATABASE IF NOT EXISTS Pictures;

USE Pictures;

CREATE TABLE IF NOT EXISTS pictures (
            id INT NOT NULL AUTO_INCREMENT,
            path VARCHAR(255),
            date DATETIME,
            PRIMARY KEY (id)
        );


CREATE TABLE IF NOT EXISTS tags (
            tag VARCHAR(32),
            picture_id INT,
            confidence FLOAT,
            date DATETIME,
            PRIMARY KEY (tag, picture_id),
            FOREIGN KEY (picture_id) REFERENCES pictures(id)
        );
