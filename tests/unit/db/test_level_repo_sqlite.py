import pytest

from frayerstore.db.sqlite.level_repo_sqlite import SQLiteLevelRepository
from frayerstore.db.sqlite.level_mapper import LevelMapper
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------


@pytest.fixture
def conn(schema_db):
    """
    Uses your existing schema_db fixture (with Levels table created).
    """
    return schema_db


@pytest.fixture
def mapper():
    return LevelMapper()


@pytest.fixture
def repo(conn, mapper):
    return SQLiteLevelRepository(conn, mapper)


# Helper: insert a row manually for testing lookups
def insert_row(conn, *, name, slug):
    q = """
    INSERT INTO Levels (name, slug)
    VALUES (?, ?)
    RETURNING id, name, slug
    """
    return conn.execute(
        q,
        (
            name,
            slug,
        ),
    ).fetchone()


# ---------------------------------------------------------------------------
# TESTS FOR CREATE()
# ---------------------------------------------------------------------------


def test_create_inserts_row_and_returns_domain(conn, repo, mapper):
    data = LevelCreate(
        name="KS4",
        slug="ks4",
    )

    created = repo.create(data)

    # Check row exists in DB
    row = conn.execute("SELECT * FROM Levels WHERE slug='ks4'").fetchone()
    assert row is not None
    assert row["name"] == "KS4"

    # Check mapper returned a Level instance
    assert isinstance(created, Level)
    assert created.slug == "ks4"
    assert created.pk == row["id"]


def test_create_uses_mapper_to_generate_params(repo, mapper, conn, monkeypatch):
    """
    Verify that create_to_params() is actually used.
    """
    called = {}

    def fake_params(data):
        called["params"] = True
        return ("A", "a")

    monkeypatch.setattr(mapper, "create_to_params", fake_params)

    data = LevelCreate(name="X", slug="x")
    repo.create(data)

    assert called.get("params", False) is True


# ---------------------------------------------------------------------------
# TESTS FOR get_by_slug()
# ---------------------------------------------------------------------------


def test_get_by_slug_finds_row(repo, conn):
    row = insert_row(conn, name="KS4", slug="ks4")

    level = repo.get_by_slug("ks4")
    assert isinstance(level, Level)
    assert level.pk == row["id"]
    assert level.slug == "ks4"


def test_get_by_slug_returns_none_if_not_found(repo):
    assert repo.get_by_slug("missing") is None


# ---------------------------------------------------------------------------
# TESTS FOR get_by_name()
# ---------------------------------------------------------------------------


def test_get_by_name_finds_row(repo, conn):
    row = insert_row(
        conn,
        name="KS5",
        slug="ks5",
    )

    level = repo.get_by_name("KS5")
    assert isinstance(level, Level)
    assert level.pk == row["id"]
    assert level.name == "KS5"


def test_get_by_name_returns_none_if_not_found(repo):
    assert repo.get_by_name("Nope") is None


# ---------------------------------------------------------------------------
# TESTS FOR get_by_id()
# ---------------------------------------------------------------------------


def test_get_by_id_finds_row(repo, conn):
    row = insert_row(
        conn,
        name="Y12",
        slug="y12",
    )

    level = repo.get_by_id(row["id"])
    assert isinstance(level, Level)
    assert level.pk == row["id"]
    assert level.slug == "y12"


def test_get_by_id_returns_none_if_not_found(repo):
    assert repo.get_by_id(9999) is None
