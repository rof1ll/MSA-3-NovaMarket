import logging
import time

import gevent
from locust import HttpUser, constant, task

LOGGER = logging.getLogger("locust.circuit_breaker")


class CircuitBreakerUser(HttpUser):
    wait_time = constant(0)

    def on_start(self) -> None:
        self.phase = "trip"
        self.error_requests_sent = 0
        self.recovery_check_at = 0.0
        LOGGER.info("Starting Circuit Breaker test...")

    @task
    def run_scenario(self) -> None:
        if self.phase == "trip":
            with self.client.get(
                "/logistics/unavailable",
                name="Trip breaker: /logistics/unavailable",
                catch_response=True,
            ) as response:
                if response.status_code in (500, 503):
                    response.success()
                else:
                    response.failure(f"Expected 500/503 during tripping, got {response.status_code}.")
            self.error_requests_sent += 1
            if self.error_requests_sent >= 7:
                LOGGER.info("Sent %s error requests. Checking OPEN state.", self.error_requests_sent)
                self.phase = "open_check"
            return

        if self.phase == "open_check":
            with self.client.get(
                "/logistics/fast",
                name="Check OPEN: /logistics/fast",
                catch_response=True,
            ) as response:
                if response.status_code == 503 and response.headers.get("X-Circuit-Breaker", "").lower() == "open":
                    LOGGER.info("Circuit Breaker activated under load")
                    LOGGER.info("Circuit breaker OPEN confirmed: fallback was returned.")
                    response.success()
                    self.recovery_check_at = time.time() + 31
                    self.phase = "wait_recovery"
                else:
                    response.failure(
                        f"Expected fallback 503 with X-Circuit-Breaker=open, got {response.status_code} "
                        f"and header '{response.headers.get('X-Circuit-Breaker', '')}'."
                    )
                    self.phase = "trip"
                    self.error_requests_sent = 0
            return

        if self.phase == "wait_recovery":
            if time.time() < self.recovery_check_at:
                gevent.sleep(1)
                return
            self.phase = "recovery_check"

        if self.phase == "recovery_check":
            with self.client.get(
                "/logistics/fast",
                name="Check recovery: /logistics/fast",
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    LOGGER.info("Circuit breaker recovery confirmed: backend is reachable again.")
                    response.success()
                else:
                    response.failure(f"Expected 200 after recovery window, got {response.status_code}.")

            self.phase = "trip"
            self.error_requests_sent = 0
