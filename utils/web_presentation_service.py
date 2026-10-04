"""
Web Presentation Service for Thomas Young Simulator.
Runs a lightweight, embedded Flask presentation server on a background daemon thread
and automatically launches the interactive presentation deck in the default web browser.
"""

import os
import sys
import socket
import logging
import threading
import time
import webbrowser
from typing import Optional


class WebPresentationService:
    """Manages the background Flask daemon server and web browser dispatch."""

    _instance: Optional["WebPresentationService"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._server_thread: Optional[threading.Thread] = None
        self._server = None
        self._port: Optional[int] = None
        self._host: str = "127.0.0.1"
        self._is_running: bool = False
        self._ready_event = threading.Event()

    @classmethod
    def get_instance(cls) -> "WebPresentationService":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    @staticmethod
    def find_free_port(start_port: int = 5055, max_attempts: int = 50) -> int:
        """Finds an available local port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    def start_server(self, port: Optional[int] = None, host: str = "127.0.0.1") -> int:
        """Starts the Flask presentation app in a background daemon thread."""
        with self._lock:
            if self._is_running and self._port is not None:
                return self._port

            self._host = host
            self._port = port if port is not None else self.find_free_port(start_port=5055)
            self._ready_event.clear()

            from web.app import create_app
            app = create_app()

            # Suppress standard werkzeug access logs to keep terminal output clean
            log = logging.getLogger("werkzeug")
            log.setLevel(logging.ERROR)

            from werkzeug.serving import make_server
            self._server = make_server(self._host, self._port, app, threaded=True)

            def _serve():
                self._ready_event.set()
                try:
                    self._server.serve_forever()
                except Exception as e:
                    print(f"Web presentation daemon error: {e}")
                finally:
                    self._is_running = False

            self._server_thread = threading.Thread(
                target=_serve,
                daemon=True,
                name="WebPresentationDaemon"
            )
            self._server_thread.start()
            self._is_running = True

            self._ready_event.wait(timeout=2.0)
            return self._port

    def get_url(self, section: Optional[str] = None) -> str:
        """Returns the local URL for the web presentation."""
        if not self._is_running or self._port is None:
            self.start_server()
        base = f"http://{self._host}:{self._port}/"
        if section:
            return f"{base}#{section}"
        return base

    @classmethod
    def open_in_browser(cls, section: Optional[str] = None) -> bool:
        """Launches the interactive web presentation in the default browser."""
        service = cls.get_instance()
        try:
            url = service.get_url(section=section)
            webbrowser.open_new_tab(url)
            return True
        except Exception as e:
            print(f"Failed to open web presentation in browser: {e}")
            return False

    def stop_server(self):
        """Stops the daemon server cleanly."""
        with self._lock:
            if self._server:
                try:
                    self._server.shutdown()
                except Exception:
                    pass
                self._server = None
            self._is_running = False
