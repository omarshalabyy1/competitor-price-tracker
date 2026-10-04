"""Competitor prices, once a week: load the reference data, collect the week's competitor prices,
match them to our products, and email an alert when a competitor undercuts a key product.

Each run covers one week (its data interval). Unpaused for the first time, Airflow runs every week
since start_date one after another, so the grocery price history is loaded week by week, exactly
as the weekly schedule would have seen it. Web shop pages only show today's price, so they are
read, and the alert emailed, on the latest run only (LatestOnlyOperator skips them on older weeks).
"""

from datetime import datetime, timedelta, timezone

from airflow.providers.standard.operators.latest_only import LatestOnlyOperator
from airflow.sdk import dag, task
from airflow.timetables.interval import DeltaDataIntervalTimetable

import tracker


@dag(
    # Each run covers the week before it (its data interval). Said explicitly: since Airflow 3 a
    # plain timedelta schedule gives runs no interval.
    schedule=DeltaDataIntervalTimetable(timedelta(weeks=1)),
    start_date=datetime(2025, 9, 7, tzinfo=timezone.utc),  # a Sunday: every run covers Sunday to Sunday
    catchup=True,
    max_active_runs=1,  # weeks in order, so each change is caught by the first run that has both prices
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
)
def competitor_prices():
    @task
    def load_reference():
        tracker.load_reference()

    @task
    def collect_open_prices(data_interval_start=None, data_interval_end=None):
        tracker.collect_open_prices(data_interval_start, data_interval_end)

    @task
    def collect_web_shops(data_interval_start=None):
        tracker.collect_web_shops(data_interval_start.date())

    @task(trigger_rule="none_failed")  # still runs on older weeks, when collect_web_shops is skipped
    def match():
        tracker.match()

    @task
    def send_alert(data_interval_start=None):
        tracker.send_alert(data_interval_start.date())

    latest_only = LatestOnlyOperator(task_id="latest_only")
    reference, grocery, web_shops, matched, alert = (
        load_reference(), collect_open_prices(), collect_web_shops(), match(), send_alert()
    )

    reference >> [grocery, web_shops] >> matched >> alert
    latest_only >> [web_shops, alert]


competitor_prices()
