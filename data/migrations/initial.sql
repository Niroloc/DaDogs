CREATE TABLE IF NOT EXISTS dogs
    (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
    );

CREATE TABLE IF NOT EXISTS walks
    (
    id INTEGER PRIMARY KEY,
    dt DATE NOT NULL,
    ts time NOT NULL,
    quantity INTEGER NOT NULL,
    dog_id INTEGER,
    FOREIGN KEY(dog_id) REFERENCES dogs(id)
    );
