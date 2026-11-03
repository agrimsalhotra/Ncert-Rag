import io
import logging
import sys


def configure_utf8_output():
    """Ensure standard output and standard error handle Unicode characters (e.g. chemical arrows, Greek letters) without encoding errors on Windows."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    elif hasattr(sys.stdout, "buffer"):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass

    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    elif hasattr(sys.stderr, "buffer"):
        try:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure basic logging and ensure UTF-8 output."""
    configure_utf8_output()
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("ncert_rag")


# Auto-configure UTF-8 encoding on import
configure_utf8_output()
