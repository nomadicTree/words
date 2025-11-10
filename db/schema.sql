CREATE TABLE Subjects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
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
    level_id INTEGER REFERENCES Levels(id),   -- optional metadata
    UNIQUE(name, subject_id)
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
    synonyms TEXT,
    UNIQUE(word, subject_id)
);

CREATE TABLE WordVersions (
    id INTEGER PRIMARY KEY,
    word_id INTEGER NOT NULL REFERENCES Words(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES Courses(id) ON DELETE CASCADE,
    definition TEXT,
    characteristics TEXT,
    examples TEXT,
    non_examples TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(word_id, course_id)
);

CREATE TABLE WordVersionContexts (
    word_version_id INTEGER NOT NULL REFERENCES WordVersions(id) ON DELETE CASCADE,
    topic_id INTEGER NOT NULL REFERENCES Topics(id) ON DELETE CASCADE,
    PRIMARY KEY (word_version_id, topic_id)
);
