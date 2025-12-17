"""Модуль для управления контекстом логирования (trace_id)."""

from contextvars import ContextVar


trace_id_var: ContextVar[str] = ContextVar("trace_id", default="no_trace_id")
