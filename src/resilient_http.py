from __future__ import annotations

import logging
from dataclasses import dataclass, field
from time import sleep
from typing import Any

import requests


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 1.0
    retryable_status_codes: set[int] = field(default_factory=lambda: {429, 500, 502, 503, 504})


DEFAULT_RETRY_POLICY = RetryPolicy()


def request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    *,
    logger: logging.Logger,
    operation: str,
    retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    raise_for_status: bool = True,
    **kwargs: Any,
) -> requests.Response:
    caller = getattr(session, method.lower())
    last_response: requests.Response | None = None
    last_error: Exception | None = None

    for attempt in range(1, retry_policy.max_attempts + 1):
        try:
            response = caller(url, **kwargs)
            last_response = response
            status_code = getattr(response, "status_code", 200)
            if status_code in retry_policy.retryable_status_codes and attempt < retry_policy.max_attempts:
                logger.warning(
                    "HTTP retry agendado após status retornável.",
                    extra={
                        "operation": operation,
                        "http_method": method.upper(),
                        "url": url,
                        "status_code": status_code,
                        "attempt": attempt,
                        "max_attempts": retry_policy.max_attempts,
                    },
                )
                if retry_policy.backoff_seconds > 0:
                    sleep(retry_policy.backoff_seconds * attempt)
                continue
            if raise_for_status:
                response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            if attempt >= retry_policy.max_attempts:
                break
            logger.warning(
                "HTTP retry agendado após exceção de transporte.",
                extra={
                    "operation": operation,
                    "http_method": method.upper(),
                    "url": url,
                    "attempt": attempt,
                    "max_attempts": retry_policy.max_attempts,
                    "error_type": type(exc).__name__,
                },
            )
            if retry_policy.backoff_seconds > 0:
                sleep(retry_policy.backoff_seconds * attempt)

    if last_response is not None:
        if raise_for_status:
            last_response.raise_for_status()
        return last_response
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Falha inesperada sem resposta nem exceção em {operation}.")
