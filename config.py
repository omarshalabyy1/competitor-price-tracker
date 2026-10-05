"""The one place client values come from: config/client.yaml, plus the secrets in .env."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).parent
REQUIRED = [
    "client.name", "client.currency",
    "warehouse.host", "warehouse.port", "warehouse.database", "warehouse.user",
    "inputs.catalogue", "competitors",
    "rules.match_threshold", "rules.undercut_pct",
    "schedule.cron", "schedule.timezone", "schedule.start_date",
    "alert.to",
    "report.title",
    "report.colours.data", "report.colours.text", "report.colours.muted",
    "report.colours.page", "report.colours.line", "report.colours.danger",
]


def load_config():
    cfg = yaml.safe_load((ROOT / "config" / "client.yaml").read_text(encoding="utf-8"))
    for key in REQUIRED:
        node = cfg
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                raise SystemExit(f"config/client.yaml is missing {key}")
            node = node[part]
    for store in cfg["competitors"]:
        if not {"id", "name", "kind", "city"} <= store.keys() or ("parser" in store) == ("open_prices_location" in store):
            raise SystemExit(f"config/client.yaml competitor {store.get('id', '?')}: needs id, name, kind, city, "
                             "and either parser and pages or open_prices_location")

    load_dotenv(ROOT / ".env")
    if not os.environ.get("DB_PASSWORD"):
        raise SystemExit(".env is missing DB_PASSWORD (copy .env.example to .env)")

    # Inside the Docker network the warehouse is reached by its service name, not 127.0.0.1;
    # docker-compose.yml sets these two for the Airflow container.
    w = cfg["warehouse"]
    w["host"] = os.environ.get("WAREHOUSE_HOST", w["host"])
    w["port"] = int(os.environ.get("WAREHOUSE_PORT", w["port"]))
    w["password"] = os.environ["DB_PASSWORD"]
    cfg["input_dir"] = ROOT / "data" / "input"
    return cfg
