"""
Session Manager for QrypTalk Quantum Key Distribution.
Tracks distributed shared keys, active QML security status, QBER metrics, and telemetry history.
"""

from typing import Optional, Dict, Any, List
import time


class SessionManager:
    """Manages active cryptographic sessions and quantum channel telemetry."""

    def __init__(self):
        self.key: Optional[str] = None
        self.qber: Optional[float] = None
        self.status: str = "Uninitialized"
        self.qml_telemetry: Optional[Dict[str, Any]] = None
        self.last_updated: float = time.time()
        self.session_history: List[Dict[str, Any]] = []

    def update_session(
        self,
        key: Optional[str],
        qber: float,
        status: str,
        qml_telemetry: Optional[Dict[str, Any]] = None,
    ):
        """Updates the current active session state."""
        self.key = key
        self.qber = qber
        self.status = status
        self.qml_telemetry = qml_telemetry
        self.last_updated = time.time()

        record = {
            "timestamp": self.last_updated,
            "qber": round(qber, 4),
            "status": status,
            "has_key": bool(key is not None),
            "qml_classification": qml_telemetry.get("predicted_class") if qml_telemetry else None,
            "is_secure": qml_telemetry.get("is_secure") if qml_telemetry else (qber < 0.15),
        }
        self.session_history.append(record)
        # Keep last 50 session exchanges
        if len(self.session_history) > 50:
            self.session_history.pop(0)

    def reset(self):
        """Clears the active session keys."""
        self.key = None
        self.qber = None
        self.status = "Reset"
        self.qml_telemetry = None


# Global singleton instance
session_manager = SessionManager()
