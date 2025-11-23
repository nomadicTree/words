from __future__ import annotations
import sqlite3
from typing import Any
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate
from frayerstore.db.interfaces.subject_repo import SubjectRepository
from frayerstore.db.interfaces.course_repo import CourseRepository
from frayerstore.db.sqlite.subject_mapper import SubjectMapper


class SQLiteSubjectRepository(SubjectRepository):
    def __init__(
        self,
        conn: sqlite3.Connection,
        subject_mapper: SubjectMapper,
        course_repo: CourseRepository | None = None,
    ) -> SQLiteSubjectRepository:
        self.conn = conn
        self.subject_mapper = subject_mapper
        self.course_repo = course_repo

    def _get_one(
        self, where: str, param: Any, include_courses: bool, include_topics: bool
    ) -> Subject | None:
        """
        Internal lookup helper for all Subject retrieval methods.

        Hydration behaviour:
        - If include_courses=False:
            subject.courses will be an empty list.

        - If include_courses=True:
            subject.courses will contain a fully hydrated list of Course objects.

        - If include_courses=True and include_topics=True:
            each Course in subject.courses will have its .topics list
            populated with fully hydrated Topic objects.

        - If include_courses=True and include_topics=False:
            each Course will have topics=[], as topics are not hydrated.

        Returns None if no subject matches the condition.
        """
        q = f"""
            SELECT id, name, slug
            FROM Subjects
            WHERE {where}
        """

        row = self.conn.execute(q, (param,)).fetchone()
        if not row:
            return None

        subject = self.subject_mapper.row_to_domain(row)

        if include_courses:
            if not self.course_repo:
                raise ValueError("course_repo is required when include_courses=True")
            subject.courses = self.course_repo.get_for_subject(
                subject.pk, include_topics=include_topics
            )

        return subject

    def _get_many(
        self,
        where: str | None = None,
        params: tuple = (),
        include_courses: bool = False,
        include_topics: bool = False,
    ) -> list[Subject]:
        """
        Internal helper for retrieving multiple Subject objects.

        Hydration behaviour:
        - If include_courses=False:
            subject.courses will be empty.
        - If include_courses=True:
            subject.courses will contain hydrated Course objects.
        - If include_courses=True and include_topics=True:
            each course.topics will contain fully hydrated Topics.

        Results are ordered alphabetically by subject name.
        """
        base_q = """
            SELECT
                id,
                name,
                slug
            FROM Subjects
        """

        if where:
            q = f"{base_q} WHERE {where}"
        else:
            q = base_q

        q += " ORDER BY name ASC"

        rows = self.conn.execute(q, params).fetchall()
        subjects = [self.subject_mapper.row_to_domain(r) for r in rows]

        if include_courses:
            if not self.course_repo:
                raise ValueError("course_repo is required when include_courses=True")
            for subject in subjects:
                subject.courses = self.course_repo.get_for_subject(
                    subject.pk,
                    include_topics=include_topics,
                )

        return subjects

    def get_by_slug(
        self, slug: str, include_courses: bool = False, include_topics: bool = False
    ) -> Subject:
        """Retrieve a Subject by slug."""
        return self._get_one(
            "slug = ?",
            slug,
            include_courses,
            include_topics,
        )

    def get_by_name(
        self,
        name: str,
        include_courses: bool = False,
        include_topics: bool = False,
    ) -> Subject | None:
        """Retrieve a Subject by name."""
        return self._get_one(
            "name = ?",
            name,
            include_courses,
            include_topics,
        )

    def get_by_id(
        self,
        id: int,
        include_courses: bool = False,
        include_topics: bool = False,
    ) -> Subject | None:
        """Retrieve a Subject by id."""
        return self._get_one(
            "id = ?",
            id,
            include_courses,
            include_topics,
        )

    def list_all(
        self,
        include_courses: bool = False,
        include_topics: bool = False,
    ) -> list[Subject]:
        """Return all subjects."""
        return self._get_many(
            include_courses=include_courses,
            include_topics=include_topics,
        )

    def create(self, data: SubjectCreate) -> Subject:
        """Insert new row for SubjectCreate."""
        params = self.subject_mapper.create_to_params(data)
        q = """
        INSERT INTO Subjects (name, slug)
        VALUES (?, ?)
        RETURNING id, name, slug
        """
        row = self.conn.execute(q, params).fetchone()
        return self.subject_mapper.row_to_domain(row)
