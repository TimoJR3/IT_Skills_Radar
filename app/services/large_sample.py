from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any


ROLE_TEMPLATES: list[dict[str, Any]] = [
    {
        "role": "Junior Data Scientist",
        "titles": [
            "Junior Data Scientist",
            "Data Scientist / ML",
            "Junior ML Research Analyst",
        ],
        "base_salary": 155_000,
        "skills": [
            "Python",
            "pandas",
            "NumPy",
            "sklearn",
            "SQL",
            "Postgres",
            "machine learning",
            "Git",
        ],
    },
    {
        "role": "Data Analyst",
        "titles": [
            "Data Analyst",
            "Junior Data Analyst",
            "BI Data Analyst",
        ],
        "base_salary": 125_000,
        "skills": [
            "SQL",
            "PostgreSQL",
            "Python",
            "pandas",
            "dashboard",
            "Power BI",
            "GitHub",
        ],
    },
    {
        "role": "Product Analyst",
        "titles": [
            "Product Analyst",
            "Junior Product Analyst",
            "Product Data Analyst",
        ],
        "base_salary": 140_000,
        "skills": [
            "SQL",
            "A/B testing",
            "AB test",
            "experimentation",
            "dashboard",
            "Python",
            "BI",
        ],
    },
    {
        "role": "ML Engineer",
        "titles": [
            "ML Engineer",
            "Machine Learning Engineer",
            "Junior ML Engineer",
        ],
        "base_salary": 190_000,
        "skills": [
            "Python",
            "ML",
            "machine learning",
            "scikit-learn",
            "SQL",
            "Git",
            "Postgres",
        ],
    },
    {
        "role": "Intern Analyst",
        "titles": [
            "Data Analyst Intern",
            "Product Analyst Intern",
            "Intern Data/Product Analyst",
        ],
        "base_salary": 70_000,
        "skills": [
            "SQL",
            "Python",
            "pandas",
            "dashboard",
            "A/B testing",
            "GitHub",
        ],
    },
]

CITIES = [
    "Moscow, Russia",
    "Saint Petersburg, Russia",
    "Kazan, Russia",
    "Novosibirsk, Russia",
    "Yekaterinburg, Russia",
    "Remote, Russia",
]
COMPANIES = [
    "DataBridge",
    "ProductFlow",
    "MarketMind",
    "Signal AI",
    "RetailTech",
    "FinData",
    "SearchLab",
    "CloudMetrics",
]
WORK_FORMATS = ["remote", "hybrid", "office"]
EMPLOYMENT_TYPES = ["full_time", "full_time", "full_time", "internship"]


def _pick_skills(rng: random.Random, pool: list[str]) -> list[str]:
    count = rng.randint(3, min(6, len(pool)))
    skills = rng.sample(pool, count)
    if "SQL" not in skills and rng.random() < 0.72:
        skills.append("SQL")
    if "Python" not in skills and rng.random() < 0.58:
        skills.append("Python")
    return sorted(set(skills))


def _seniority_from_title(title: str, rng: random.Random) -> str:
    lowered = title.lower()
    if "intern" in lowered:
        return "intern"
    if "junior" in lowered:
        return "junior"
    return rng.choices(
        ["junior", "middle", "unknown"],
        weights=[0.45, 0.4, 0.15],
        k=1,
    )[0]


def _salary(
    rng: random.Random,
    base_salary: int,
    seniority: str,
) -> tuple[int | None, int | None]:
    if rng.random() < 0.27:
        return None, None

    multiplier = {
        "intern": 0.55,
        "junior": 0.85,
        "middle": 1.25,
        "unknown": 1.0,
    }.get(seniority, 1.0)
    center = int(base_salary * multiplier * rng.uniform(0.88, 1.18))
    spread = rng.randint(20_000, 65_000)
    return max(35_000, center - spread // 2), center + spread // 2


def generate_records(count: int = 10_000, seed: int = 42) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    start_date = datetime(2025, 1, 1, 9, 0, 0)
    records: list[dict[str, Any]] = []

    for index in range(1, count + 1):
        template = rng.choice(ROLE_TEMPLATES)
        title = rng.choice(template["titles"])
        seniority = _seniority_from_title(title, rng)
        skills = _pick_skills(rng, template["skills"])
        salary_from, salary_to = _salary(
            rng,
            int(template["base_salary"]),
            seniority,
        )
        published_at = start_date + timedelta(
            days=rng.randint(0, 480),
            hours=rng.randint(0, 12),
            minutes=rng.randint(0, 59),
        )
        description = (
            f"Role requires {', '.join(skills)}. "
            "Candidate will clean data, validate metrics, build analytics "
            "and communicate insights to product and business teams."
        )
        record: dict[str, Any] = {
            "id": f"large-{index:05d}",
            "title": title,
            "role": template["role"],
            "company": rng.choice(COMPANIES),
            "location": rng.choice(CITIES),
            "description": description,
            "skills": skills if index % 3 else "; ".join(skills),
            "published_at": published_at.isoformat() + "+03:00",
            "currency": "RUB",
            "gross_type": rng.choice(["gross", "net", "unknown"]),
            "salary_period": "month",
            "url": f"https://example.local/large-load-test/{index:05d}",
            "employment_type": rng.choice(EMPLOYMENT_TYPES),
            "work_format": rng.choice(WORK_FORMATS),
        }
        if salary_from is not None:
            record["salary_from"] = salary_from
        if salary_to is not None:
            record["salary_to"] = salary_to
        records.append(record)

    return records


def write_records(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a large realistic vacancy sample for load checks."
    )
    parser.add_argument("--rows", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/generated/large_vacancies_10000.json"),
    )
    args = parser.parse_args()

    records = generate_records(count=args.rows, seed=args.seed)
    write_records(records, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "rows": len(records),
                "seed": args.seed,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
