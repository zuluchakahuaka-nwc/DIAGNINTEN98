"""Вкладки приложения (представления)."""

from .faults import FaultsTab
from .rcm import RcmTab
from .report import ReportTab
from .usb_monitor import UsbMonitorTab

__all__ = ["FaultsTab", "RcmTab", "ReportTab", "UsbMonitorTab"]
