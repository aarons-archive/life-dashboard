import asyncio
import contextlib
import importlib
import logging
import logging.handlers
import os
import sys

import aiohttp.web
import aiohttp_jinja2
import aiohttp_session.redis_storage
import jinja2
import setproctitle

from core import app, config


RESET = "\u001b[0m"
BOLD = "\u001b[1m"
UNDERLINE = "\u001b[4m"
REVERSE = "\u001b[7m"
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = [f"\u001b[{30 + i}m" for i in range(8)]


@contextlib.contextmanager
def logger():
    loggers: dict[str, logging.Logger] = {
        "dashboard":    logging.getLogger("dashboard"),
        "utilities":        logging.getLogger("utilities"),
        "aiohttp": logging.getLogger("aiohttp"),

    }

    for name, log in loggers.items():

        file_handler = logging.handlers.RotatingFileHandler(
            filename=f"logs/{name}.log",
            mode="w", backupCount=5,
            encoding="utf-8",
            maxBytes=2 ** 22
        )
        log.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        log.addHandler(stream_handler)

        if os.path.isfile(f"logs/{name}.log"):
            file_handler.doRollover()

        file_formatter = logging.Formatter(
            fmt="%(asctime)s [%(name) 30s] [%(filename) 20s] [%(levelname) 7s] %(message)s", datefmt="%I:%M:%S %p %d/%m/%Y"
        )
        file_handler.setFormatter(file_formatter)

        stream_formatter = logging.Formatter(
            fmt=f"{CYAN}%(asctime)s{RESET} {YELLOW}[%(name) 30s]{RESET} {GREEN}[%(filename) 20s]{RESET} {BOLD}{REVERSE}{MAGENTA}[%(levelname) 7s]{RESET} "
                f"%(message)s",
            datefmt="%I:%M:%S %p %d/%m/%Y"
        )
        stream_handler.setFormatter(stream_formatter)

    loggers["dashboard"].setLevel(logging.INFO)
    loggers["utilities"].setLevel(logging.DEBUG)
    loggers["aiohttp"].setLevel(logging.DEBUG)

    try:
        yield
    finally:
        [log.handlers[0].close() for log in loggers.values()]


if __name__ == "__main__":

    setproctitle.setproctitle("Dashboard")

    try:
        import uvloop
        if sys.platform != 'win32':
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        uvloop = None
    else:
        del uvloop

    with logger():

        app = app.Dashboard()

        endpoints = ["index", "login", "api.callback"]
        for endpoint in [importlib.import_module(f"endpoints.{endpoint}") for endpoint in endpoints]:
            endpoint.setup(app=app)

        app.add_routes(
            [aiohttp.web.static("/static", os.path.abspath(os.path.join(os.path.dirname(__file__), "static")), show_index=True, follow_symlinks=True)]
        )
        app["static_root_url"] = "/static"

        aiohttp_jinja2.setup(
            app=app,
            loader=jinja2.FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), "templates")))
        )

        aiohttp.web.run_app(
            app=app,
            host=config.HOST,
            port=config.PORT
        )
