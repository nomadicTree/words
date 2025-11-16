CREATE TABLE Subjects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE
);

CREATE TABLE Levels (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE Courses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    subject_id INTEGER NOT NULL REFERENCES Subjects(id),
    level_id INTEGER NOT NULL REFERENCES Levels(id),
    slug TEXT NOT NULL,
    UNIQUE(name, subject_id),
    UNIQUE(slug, subject_id)
);

CREATE TABLE Topics (
    id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES Courses(id),
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    UNIQUE(course_id, code)
);

CREATE TABLE Words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    subject_id INTEGER NOT NULL REFERENCES Subjects(id),
    slug TEXT NOT NULL,
    UNIQUE(word, subject_id),
    UNIQUE(subject_id, slug)
);

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

CREATE TABLE Synonyms (
    id INTEGER PRIMARY KEY,
    word_id INTEGER NOT NULL REFERENCES Words(id) ON DELETE CASCADE,
    synonym TEXT NOT NULL,
    UNIQUE(word_id, synonym)
);

CREATE TABLE WordRelationships (
    id INTEGER PRIMARY KEY,
    word_id1 INTEGER NOT NULL REFERENCES Words(id) ON DELETE CASCADE,
    word_id2 INTEGER NOT NULL REFERENCES Words(id) ON DELETE CASCADE,
    CHECK (word_id1 != word_id2),
    CHECK (word_id1 < word_id2),
    UNIQUE (word_id1, word_id2)
);

CREATE VIEW vw_WordDetails AS
SELECT DISTINCT
    w.id          AS word_id,
    w.word        AS word,
    w.slug        AS word_slug,

    s.id          AS subject_id,
    s.name        AS subject_name,
    s.slug        AS subject_slug,

    l.id          AS level_id,
    l.name        AS level_name,

    c.id          AS course_id,
    c.name        AS course_name,
    c.slug        AS course_slug,

    t.id          AS topic_id,
    t.name        AS topic_name,
    t.code        AS topic_code

FROM Words w
JOIN Subjects s ON w.subject_id = s.id
JOIN WordVersions wv ON wv.word_id = w.id

LEFT JOIN WordVersionLevels wvl ON wvl.word_version_id = wv.id
LEFT JOIN Levels l ON wvl.level_id = l.id

LEFT JOIN WordVersionContexts wvc ON wvc.word_version_id = wv.id
LEFT JOIN Topics t ON wvc.topic_id = t.id

LEFT JOIN Courses c ON t.course_id = c.id;

-- Search view --
CREATE VIEW vw_SearchWordVersions AS
SELECT
    w.id AS word_id,
    w.word AS word,
    w.slug AS word_slug,

    sub.id AS subject_id,
    sub.name AS subject_name,
    sub.slug AS subject_slug,

    -- synonyms (comma-separated, distinct)
    GROUP_CONCAT(DISTINCT syn.synonym) AS synonyms,

    -- searchable text: word + synonyms (spaces)
    w.word || ' ' ||
    COALESCE(REPLACE(GROUP_CONCAT(DISTINCT syn.synonym), ',', ' '), '')
    AS search_text,

    v.id AS version_id,
    v.definition AS version_definition,

    -- level names (comma-separated; DISTINCT allowed, ORDER BY not allowed)
    GROUP_CONCAT(DISTINCT lvl.name) AS level_names

FROM Words w
JOIN Subjects sub
    ON sub.id = w.subject_id

LEFT JOIN Synonyms syn
    ON syn.word_id = w.id

JOIN WordVersions v
    ON v.word_id = w.id

JOIN WordVersionLevels wvl
    ON wvl.word_version_id = v.id

JOIN Levels lvl
    ON lvl.id = wvl.level_id

GROUP BY
    w.id,
    v.id;