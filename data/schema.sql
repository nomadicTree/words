CREATE TABLE Word (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    subject_id INTEGER NOT NULL REFERENCES Subject(id),
    definition TEXT,
    characteristics TEXT,
    examples TEXT,
    non_examples TEXT
);

CREATE TABLE Subject (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE Course (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    subject_id INTEGER NOT NULL REFERENCES Subject(id),
    UNIQUE(name, subject_id)
);

CREATE TABLE Topic (
    id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES Course(id),
    code TEXT NOT NULL,
    name TEXT,
    UNIQUE(course_id, code)
);

CREATE TABLE WordTopic (
    word_id INTEGER NOT NULL REFERENCES Word(id) ON DELETE CASCADE,
    topic_id INTEGER NOT NULL REFERENCES Topic(id) ON DELETE CASCADE,
    PRIMARY KEY(word_id, topic_id)
);