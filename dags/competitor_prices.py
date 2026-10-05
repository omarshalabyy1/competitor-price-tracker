"""Competitor prices, once a week: load the reference data, collect the week's competitor prices,
match them to our products, and email an alert when a competitor undercuts a key product.

Each run covers one week (its data interval). Unpaused for the first time, Airflow runs every week
since schedule.start_date one after another, so the grocery price history is loaded week by week,
exactly as the weekly schedule would have seen it. Web shop pages only show today's price, so they
are read, and the alert emailed, on the latest run only (LatestOnlyOperator skips them on older
weeks). The schedule comes from config/client.yaml, read when Airflow parses this file.
"""

from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.latest_only import LatestOnlyOperator
from airflow.sdk import dag, task
from airflow.timetables.interval import CronDataIntervalTimetable

import tracker
from config import load_config

schedule = load_config()["schedule"]
TZ = schedule["timezone"]


def week_of(data_interval_start):
    """The run's week: the first day of its interval, in the client's time zone."""
    return data_interval_start.in_timezone(TZ).date()


@dag(
    # A data-interval timetable, said explicitly: since Airflow 3 a plain cron schedule gives runs no interval.
    schedule=CronDataIntervalTimetable(schedule["cron"], timezone=TZ),
    start_date=pendulum.datetime(*schedule["start_date"].timetuple()[:3], tz=TZ),
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
        tracker.collect_open_prices(data_interval_start, data_interval_end, week_of(data_interval_start))

    @task
    def collect_web_shops(data_interval_start=None):
        tracker.collect_web_shops(week_of(data_interval_start))

    @task(trigger_rule="none_failed")  # still runs on older weeks, when collect_web_shops is skipped
    def match():
        tracker.match()

    @task
    def send_alert(data_interval_start=None):
        tracker.send_alert(week_of(data_interval_start))

    latest_only = LatestOnlyOperator(task_id="latest_only")
    reference, grocery, web_shops, matched, alert = (
        load_reference(), collect_open_prices(), collect_web_shops(), match(), send_alert()
    )

    reference >> [grocery, web_shops] >> matched >> alert
    latest_only >> [web_shops, alert]


competitor_prices()
