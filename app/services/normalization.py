from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping


FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "source_vacancy_id": ("source_vacancy_id", "vacancy_id", "id"),
    "title": ("title", "vacancy_title", "name"),
    "company_name": ("company_name", "company", "employer_name"),
    "description_text": ("description_text", "description", "body"),
    "role_hint": ("role", "role_name", "role_title"),
    "seniority_level": ("seniority_level", "seniority", "level"),
    "employment_type": ("employment_type", "employment"),
    "work_format": ("work_format", "format"),
    "city": ("city",),
    "country": ("country",),
    "location": ("location",),
    "vacancy_url": ("vacancy_url", "url", "source_url"),
    "published_at": ("published_at", "publication_time", "created_at"),
    "skills": ("skills", "key_skills", "skills_raw"),
    "salary_from": ("salary_from", "compensation_from"),
    "salary_to": ("salary_to", "compensation_to"),
    "currency_code": ("currency_code", "currency"),
    "gross_type": ("gross_type", "salary_type"),
    "salary_period": ("salary_period", "compensation_period"),
}


@dataclass(frozen=True)
class RoleDefinition:
    code: str
    name: str
    group: str


@dataclass(frozen=True)
class SkillDefinition:
    slug: str
    name: str
    category: str


@dataclass(frozen=True)
class SkillMatch:
    definition: SkillDefinition
    is_required: bool
    match_source: str


@dataclass(frozen=True)
class SalaryData:
    salary_from: Decimal | None
    salary_to: Decimal | None
    currency_code: str
    gross_type: str
    salary_period: str


@dataclass(frozen=True)
class NormalizedVacancy:
    source_name: str
    source_vacancy_id: str
    role: RoleDefinition
    title: str
    company_name: str
    city: str | None
    country: str
    seniority_level: str
    employment_type: str
    work_format: str
    description_text: str | None
    vacancy_url: str | None
    published_at: datetime | None
    collected_at: datetime
    skills: list[SkillMatch]
    salary: SalaryData | None
    raw_payload: dict[str, Any]


ROLE_DEFINITIONS: dict[str, RoleDefinition] = {
    "data_scientist": RoleDefinition("data_scientist", "Data Scientist", "data"),
    "data_analyst": RoleDefinition("data_analyst", "Data Analyst", "analytics"),
    "product_analyst": RoleDefinition("product_analyst", "Product Analyst", "product"),
    "ml_engineer": RoleDefinition("ml_engineer", "ML Engineer", "ml"),
    "other_data_role": RoleDefinition("other_data_role", "Other Data Role", "data"),
}


SKILL_DEFINITIONS: dict[str, SkillDefinition] = {
    "python": SkillDefinition("python", "Python", "programming"),
    "sql": SkillDefinition("sql", "SQL", "database"),
    "postgresql": SkillDefinition("postgresql", "PostgreSQL", "database"),
    "pandas": SkillDefinition("pandas", "pandas", "analytics"),
    "numpy": SkillDefinition("numpy", "NumPy", "analytics"),
    "scikit-learn": SkillDefinition("scikit-learn", "scikit-learn", "ml"),
    "a_b_testing": SkillDefinition("a_b_testing", "A/B testing", "product_analytics"),
    "machine_learning": SkillDefinition("machine_learning", "Machine Learning", "ml"),
    "bi": SkillDefinition("bi", "BI / Visualization", "bi"),
    "git": SkillDefinition("git", "Git", "tooling"),
}


ROLE_PATTERNS: list[tuple[re.Pattern[str], RoleDefinition]] = [
    (
        re.compile(r"\bproduct\b.*\banalyst\b|\banalyst\b.*\bproduct\b"),
        ROLE_DEFINITIONS["product_analyst"],
    ),
    (
        re.compile(r"\bml engineer\b|\bmachine learning engineer\b"),
        ROLE_DEFINITIONS["ml_engineer"],
    ),
    (
        re.compile(r"\bdata scientist\b|\bscientist\b.*\bdata\b"),
        ROLE_DEFINITIONS["data_scientist"],
    ),
    (
        re.compile(r"\bdata analyst\b|\banalyst\b.*\bdata\b"),
        ROLE_DEFINITIONS["data_analyst"],
    ),
]


SENIORITY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bintern\b|\btrainee\b|\bstajer\b|\bstazher\b"), "intern"),
    (re.compile(r"\bjunior\b|\bjr\b"), "junior"),
    (re.compile(r"\bmiddle\b|\bmid\b"), "middle"),
    (re.compile(r"\bsenior\b|\bsr\b"), "senior"),
    (re.compile(r"\blead\b|\bprincipal\b"), "lead"),
]


SKILL_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "python": (re.compile(r"\bpython\b"),),
    "sql": (re.compile(r"\bsql\b"),),
    "postgresql": (re.compile(r"\bpostgres(?:ql)?\b"),),
    "pandas": (re.compile(r"\bpandas\b"),),
    "numpy": (re.compile(r"\bnumpy\b"),),
    "scikit-learn": (
        re.compile(r"\bscikit[- ]learn\b"),
        re.compile(r"\bsklearn\b"),
    ),
    "a_b_testing": (
        re.compile(r"\ba\s*/\s*b testing\b"),
        re.compile(r"\bab test(?:ing)?\b"),
        re.compile(r"\bexperimentation\b"),
        re.compile(r"\bexperiment analysis\b"),
    ),
    "machine_learning": (
        re.compile(r"\bmachine learning\b"),
        re.compile(r"\bml\b"),
    ),
    "bi": (
        re.compile(r"\bvisuali[sz]ation\b"),
        re.compile(r"\bdashboards?\b"),
        re.compile(r"\bpower bi\b"),
        re.compile(r"\btableau\b"),
        re.compile(r"\bbi\b"),
    ),
    "git": (
        re.compile(r"\bgit\b"),
        re.compile(r"\bgithub\b"),
    ),
}


HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
SKILL_SPLIT_RE = re.compile(r"[;\n|,]+")


def clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = html.unescape(str(value))
    text = HTML_TAG_RE.sub(" ", text)
    text = text.replace("\xa0", " ")
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text or None


def get_field_value(record: Mapping[str, Any], field_name: str) -> Any:
    for alias in FIELD_ALIASES[field_name]:
        if alias in record:
            value = record[alias]
            if value is None:
                continue

            if isinstance(value, str) and not clean_text(value):
                continue

            return value
    return None


def split_raw_skills(raw_value: Any) -> list[str]:
    if raw_value is None:
        return []

    if isinstance(raw_value, list):
        items = raw_value
    else:
        items = SKILL_SPLIT_RE.split(str(raw_value))

    cleaned_items: list[str] = []
    for item in items:
        cleaned = clean_text(item)
        if cleaned:
            cleaned_items.append(cleaned)
    return cleaned_items


def normalize_role(title: str, role_hint: str | None = None) -> RoleDefinition:
    search_text = " ".join(part for part in [title, role_hint] if part).lower()

    for pattern, role_definition in ROLE_PATTERNS:
        if pattern.search(search_text):
            return role_definition

    return ROLE_DEFINITIONS["other_data_role"]


def normalize_seniority(title: str, seniority_hint: str | None = None) -> str:
    search_text = " ".join(part for part in [title, seniority_hint] if part).lower()

    for pattern, normalized_value in SENIORITY_PATTERNS:
        if pattern.search(search_text):
            return normalized_value

    return "unknown"


def normalize_employment_type(value: Any) -> str:
    normalized = (clean_text(value) or "").lower()

    if normalized in {"full_time", "full-time", "full time"}:
        return "full_time"
    if normalized in {"part_time", "part-time", "part time"}:
        return "part_time"
    if normalized in {"internship", "intern"}:
        return "internship"
    if normalized in {"contract", "freelance"}:
        return "contract"
    if normalized in {"project"}:
        return "project"
    return "unknown"


def normalize_work_format(value: Any, title: str, description_text: str | None) -> str:
    normalized = (clean_text(value) or "").lower()
    search_text = " ".join(part for part in [normalized, title, description_text] if part).lower()

    if "hybrid" in search_text:
        return "hybrid"
    if "remote" in search_text:
        return "remote"
    if "office" in search_text or "onsite" in search_text:
        return "office"
    return "unknown"


def normalize_country_city(record: Mapping[str, Any]) -> tuple[str | None, str]:
    city = clean_text(get_field_value(record, "city"))
    country = clean_text(get_field_value(record, "country"))
    location = clean_text(get_field_value(record, "location"))

    if location:
        parts = [part.strip() for part in location.split(",") if part.strip()]
        if not city and parts:
            city = parts[0]
        if not country and len(parts) > 1:
            country = parts[-1]

    if not country:
        country = "Russia"

    return city, country


def parse_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    normalized = clean_text(value)
    if not normalized:
        return None

    normalized = normalized.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def parse_decimal(value: Any) -> Decimal | None:
    cleaned = clean_text(value)
    if cleaned is None:
        return None

    normalized = cleaned.replace(" ", "").replace(",", ".")
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def normalize_currency_code(value: Any) -> str:
    normalized = (clean_text(value) or "RUB").upper()
    if normalized == "RUR":
        return "RUB"
    if normalized in {"RUB", "USD", "EUR"}:
        return normalized
    return "RUB"


def normalize_gross_type(value: Any) -> str:
    normalized = (clean_text(value) or "").lower()
    if normalized in {"gross", "before_tax"}:
        return "gross"
    if normalized in {"net", "after_tax"}:
        return "net"
    return "unknown"


def normalize_salary_period(value: Any) -> str:
    normalized = (clean_text(value) or "").lower()
    if normalized in {"month", "monthly", "per_month"}:
        return "month"
    if normalized in {"year", "yearly", "per_year"}:
        return "year"
    if normalized in {"project"}:
        return "project"
    return "month"


def build_salary_data(record: Mapping[str, Any]) -> SalaryData | None:
    salary_from = parse_decimal(get_field_value(record, "salary_from"))
    salary_to = parse_decimal(get_field_value(record, "salary_to"))

    if salary_from is None and salary_to is None:
        return None

    return SalaryData(
        salary_from=salary_from,
        salary_to=salary_to,
        currency_code=normalize_currency_code(get_field_value(record, "currency_code")),
        gross_type=normalize_gross_type(get_field_value(record, "gross_type")),
        salary_period=normalize_salary_period(get_field_value(record, "salary_period")),
    )


def _collect_skill_matches(
    text_parts: Iterable[str],
    is_required: bool,
    match_source: str,
    matches: dict[str, SkillMatch],
) -> None:
    search_text = " ".join(text_parts).lower()
    if not search_text:
        return

    for slug, patterns in SKILL_PATTERNS.items():
        if not any(pattern.search(search_text) for pattern in patterns):
            continue

        current_match = matches.get(slug)
        next_match = SkillMatch(
            definition=SKILL_DEFINITIONS[slug],
            is_required=is_required,
            match_source=match_source,
        )

        if current_match is None or (is_required and not current_match.is_required):
            matches[slug] = next_match


def normalize_skills(
    title: str,
    description_text: str | None,
    raw_skills: Any,
) -> list[SkillMatch]:
    matches: dict[str, SkillMatch] = {}
    structured_skills = split_raw_skills(raw_skills)

    _collect_skill_matches(
        text_parts=structured_skills,
        is_required=True,
        match_source="manual",
        matches=matches,
    )
    _collect_skill_matches(
        text_parts=[title, description_text or ""],
        is_required=False,
        match_source="regex",
        matches=matches,
    )

    return sorted(matches.values(), key=lambda item: item.definition.slug)


def normalize_record(
    record: Mapping[str, Any],
    source_name: str,
    collected_at: datetime | None = None,
) -> NormalizedVacancy:
    title = clean_text(get_field_value(record, "title")) or ""
    company_name = clean_text(get_field_value(record, "company_name")) or ""
    description_text = clean_text(get_field_value(record, "description_text"))
    role_hint = clean_text(get_field_value(record, "role_hint"))
    seniority_hint = clean_text(get_field_value(record, "seniority_level"))
    city, country = normalize_country_city(record)

    normalized_title = title
    normalized_company_name = company_name
    published_at = parse_timestamp(get_field_value(record, "published_at"))
    normalized_collected_at = collected_at or datetime.now(timezone.utc)

    return NormalizedVacancy(
        source_name=source_name,
        source_vacancy_id=str(get_field_value(record, "source_vacancy_id")),
        role=normalize_role(title=normalized_title, role_hint=role_hint),
        title=normalized_title,
        company_name=normalized_company_name,
        city=city,
        country=country,
        seniority_level=normalize_seniority(
            title=normalized_title,
            seniority_hint=seniority_hint,
        ),
        employment_type=normalize_employment_type(get_field_value(record, "employment_type")),
        work_format=normalize_work_format(
            value=get_field_value(record, "work_format"),
            title=normalized_title,
            description_text=description_text,
        ),
        description_text=description_text,
        vacancy_url=clean_text(get_field_value(record, "vacancy_url")),
        published_at=published_at,
        collected_at=normalized_collected_at,
        skills=normalize_skills(
            title=normalized_title,
            description_text=description_text,
            raw_skills=get_field_value(record, "skills"),
        ),
        salary=build_salary_data(record),
        raw_payload=dict(record),
    )
