import logging
import logging.config
import sys
import traceback
from io import StringIO
from types import TracebackType
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple, Type

import ecs_logging
import structlog
from structlog.contextvars import merge_contextvars
from structlog.types import EventDict

# you can make it parametrizible, but INFO log level should generally be ok
LOG_LEVEL = "INFO"

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {
            "format": "%(message)s",
        },
        "log_name": {
            "format": "%(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "plain",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "watchdog": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

ExcInfo = Tuple[Type[BaseException], BaseException, Optional[TracebackType]]


def format_exc_info(logger: logging.Logger, name: str, event_dict: EventDict) -> EventDict:
    """see format_exc_info in structlog"""
    exc_info = event_dict.pop("exc_info", None)
    if exc_info:
        event_dict["error"] = _format_exception(_figure_out_exc_info(exc_info))
    return event_dict


def _format_exception(exc_info: ExcInfo):
    buffer = StringIO()
    traceback.print_exception(*exc_info, file=buffer)
    stack_trace = buffer.getvalue()
    buffer.close()
    exc_dict = {
        "type": exc_info[0].__name__,
        "message": str(exc_info[1]),
        "stack_trace": stack_trace,
    }
    code = getattr(exc_info[1], "code", None)
    if code:
        exc_dict["code"] = str(code)
    return exc_dict


def _figure_out_exc_info(v: Any) -> ExcInfo:
    """
    Depending on the Python version will try to do the smartest thing possible
    to transform *v* into an ``exc_info`` tuple.
    """
    if isinstance(v, BaseException):
        return (v.__class__, v, v.__traceback__)
    elif isinstance(v, tuple):
        return v  # type: ignore
    elif v:
        return sys.exc_info()  # type: ignore
    return v


class LogInfo:
    def __call__(self, logger: Any, name: str, event_dict: EventDict) -> EventDict:
        level = event_dict.pop("level")
        logger = event_dict.pop("logger")
        event_dict["log.level"] = level
        event_dict["log.logger"] = logger
        return event_dict


def default_processors() -> Iterable[structlog.types.Processor]:
    processors: Iterable[structlog.types.Processor] = [
        merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso", key="@timestamp"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        format_exc_info,
        LogInfo(),
        structlog.processors.UnicodeDecoder(),
        ecs_logging.StructlogFormatter(),
    ]
    return processors


class LabelBoundLogger(structlog.stdlib.BoundLogger):
    def __init__(self, *args, **kwargs):
        self.non_label_strings = {"exc_info", "event", "http", "url", "user"}
        super().__init__(*args, **kwargs)

    def _process_event(
        self, method_name: str, event: Optional[str], event_kw: Dict[str, Any]
    ) -> Tuple[Sequence[Any], Mapping[str, Any]]:
        new_event_kw: Dict[str, str] = {}
        for k, v in event_kw.items():
            if k.split(".")[0] in self.non_label_strings:
                new_event_kw[k] = v
            else:
                new_event_kw[f"labels.{k}"] = v
        return super()._process_event(method_name, event, new_event_kw)  # noqa


class StructlogHandler(logging.Handler):
    """
    Feeds all events back into structlog.
    """

    def __init__(self, *args, **kw):
        super(StructlogHandler, self).__init__(*args, **kw)
        self._log = structlog.get_logger()

    def emit(self, record):
        self._log.log(record.levelno, record.msg, name=record.name)


def setup_logging() -> None:
    logging.config.dictConfig(log_config)
    structlog.configure(
        processors=default_processors(),
        wrapper_class=LabelBoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


if __name__ == "__main__":
    # example usage
    setup_logging()

    # turn off any log propagation for libraries included in external_libraries array
    struct_handler = StructlogHandler()
    external_libraries = []
    for logger_name in external_libraries:
        logger = logging.getLogger(logger_name)
        logger.addHandler(struct_handler)
        logger.propagate = False

    log = structlog.getLogger("app")
    log.info("test %d" % 10)

