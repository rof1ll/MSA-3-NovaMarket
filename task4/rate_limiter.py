import logging

from locust import HttpUser, constant, task

LOGGER = logging.getLogger("locust.rate_limiter")
_start_logged = False
_limit_logged = False


def _log_start_once() -> None:
    global _start_logged
    if not _start_logged:
        LOGGER.info("Starting Rate Limiter test...")
        _start_logged = True


def _log_limit_once() -> None:
    global _limit_logged
    if not _limit_logged:
        LOGGER.info("Rate Limiter activated under load")
        _limit_logged = True


class WebClientUser(HttpUser):
    wait_time = constant(0)
    weight = 1

    def on_start(self) -> None:
        _log_start_once()

    @task
    def hit_web_api(self) -> None:
        with self.client.get(
            "/api/",
            headers={"Client-Type": "web"},
            name="GET /api [web]",
            catch_response=True,
        ) as response:
            if response.status_code == 429:
                _log_limit_once()
                response.failure("429 Too Many Requests")
            elif 200 <= response.status_code < 400:
                response.success()
            else:
                response.failure(f"Unexpected status {response.status_code}")


class MobileClientUser(HttpUser):
    wait_time = constant(0)
    weight = 1

    def on_start(self) -> None:
        _log_start_once()

    @task
    def hit_mobile_api(self) -> None:
        with self.client.get(
            "/api/",
            headers={"Client-Type": "mobile"},
            name="GET /api [mobile]",
            catch_response=True,
        ) as response:
            if response.status_code == 429:
                _log_limit_once()
                response.failure("429 Too Many Requests")
            elif 200 <= response.status_code < 400:
                response.success()
            else:
                response.failure(f"Unexpected status {response.status_code}")
