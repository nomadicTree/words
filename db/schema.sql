
-- -------------------------------
--  Subjects and Levels
-- -------------------------------

CREATE TABLE Subjects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE Levels (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- -------------------------------
--  Courses and Topics
-- -------------------------------

CREATE TABLE Courses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    subject_id INTEGER NOT NULL REFERENCES Subjects(id),
    level_id INTEGER REFERENCES Levels(id),  -- metadata: one course belongs to one level
    UNIQUE(name, subject_id)
);

CREATE TABLE Topics (
    id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES Courses(id),
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    UNIQUE(course_id, code)
);

-- -------------------------------
--  Words and Versions
-- -------------------------------

CREATE TABLE Words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    subject_id INTEGER NOT NULL REFERENCES Subjects(id),
    UNIQUE(word, subject_id)
);

-- WordVersions now store MEANINGS, not per-level ties
CREATE TABLE WordVersions (
    id INTEGER PRIMARY KEY,
    word_id INTEGER NOT NULL REFERENCES Words(id) ON DELETE CASCADE,
    definition TEXT,
    characteristics TEXT,
    examples TEXT,
    non_examples TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- A join table to associate a WordVersion with one or more Levels
CREATE TABLE WordVersionLevels (
    word_version_id INTEGER NOT NULL REFERENCES WordVersions(id) ON DELETE CASCADE,
    level_id INTEGER NOT NULL REFERENCES Levels(id) ON DELETE CASCADE,
    PRIMARY KEY (word_version_id, level_id)
);

-- Links each WordVersion to the Topics (and thus Courses) it appears in
CREATE TABLE WordVersionContexts (
    word_version_id INTEGER NOT NULL REFERENCES WordVersions(id) ON DELETE CASCADE,
    topic_id INTEGER NOT NULL REFERENCES Topics(id) ON DELETE CASCADE,
    PRIMARY KEY (word_version_id, topic_id)
);

-- -------------------------------
--  Word Relationships
-- -------------------------------

CREATE TABLE WordRelationships (
    id INTEGER PRIMARY KEY,
    word_id1 INTEGER NOT NULL REFERENCES Words(id) ON DELETE CASCADE,
    word_id2 INTEGER NOT NULL REFERENCES Words(id) ON DELETE CASCADE,
    CHECK (word_id1 != word_id2),
    CHECK (word_id1 < word_id2),
    UNIQUE (word_id1, word_id2)
);

-- -------------------------------
--  VIEW for easier joins
-- -------------------------------

CREATE VIEW vw_WordDetails AS
SELECT DISTINCT
    w.id          AS word_id,
    w.word        AS word,
    s.id          AS subject_id,
    s.name        AS subject_name,
    l.id          AS level_id,
    l.name        AS level_name,
    c.id          AS course_id,
    c.name        AS course_name,
    t.id          AS topic_id,
    t.name        AS topic_name
FROM Words w
JOIN Subjects s ON w.subject_id = s.id
JOIN WordVersions wv ON wv.word_id = w.id
LEFT JOIN WordVersionLevels wvl ON wvl.word_version_id = wv.id
LEFT JOIN Levels l ON wvl.level_id = l.id
LEFT JOIN WordVersionContexts wvc ON wvc.word_version_id = wv.id
LEFT JOIN Topics t ON wvc.topic_id = t.id
LEFT JOIN Courses c ON t.course_id = c.id;