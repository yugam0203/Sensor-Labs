#!/usr/bin/env python3
"""
SensorLab UI v1.1 - Adds a persistent Settings dialog (General / Device / Logging / Heater / Advanced)
Requirements: PyQt6, pyqtgraph
Run: pip install PyQt6 pyqtgraph
      python sensorlab_ui_with_settings.py
"""

import sys, os, math
from PyQt6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

APP_NAME = "SensorLab"

# ---------- Stylesheets (dark and light) ----------
DARK_STYLE = """
QWidget { background-color: #0f1419; color: #d6e1ea; font-family: 'Segoe UI', Roboto, Arial; }
QPushButton { background:#141922; border:1px solid #1f2933; padding:8px; border-radius:8px;}
QPushButton#primary { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1c75ff, stop:1 #2aa7ff); color: white; font-weight:600; }
QComboBox, QLineEdit, QTextEdit { background:#0d1115; border:1px solid #22272b; padding:6px; border-radius:6px; color:#e6eef6; }
QLabel.title { font-size:18px; font-weight:700; color:#ffffff; }
QFrame#control_panel, QFrame#meta_panel { background: #0c1014; border-radius:10px; padding:12px; }
QStatusBar { background: #0c1014; color:#9fb0c4; }
QTabBar::tab:selected { background: #10151a; border:1px solid #233142; }
"""

LIGHT_STYLE = """
QWidget { background-color: #f6f8fa; color: #1b2836; font-family: 'Segoe UI', Roboto, Arial; }
QPushButton { background:#ffffff; border:1px solid #d7e0e8; padding:8px; border-radius:8px;}
QPushButton#primary { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1c75ff, stop:1 #2aa7ff); color: white; font-weight:600; }
QComboBox, QLineEdit, QTextEdit { background:#ffffff; border:1px solid #d7e0e8; padding:6px; border-radius:6px; color:#1b2836; }
QLabel.title { font-size:18px; font-weight:700; color:#0f1720; }
QFrame#control_panel, QFrame#meta_panel { background: #ffffff; border-radius:10px; padding:12px; border:1px solid #e6eef6; }
QStatusBar { background: #ffffff; color:#556d7a; }
QTabBar::tab:selected { background: #f1f5f8; border:1px solid #e0edf6; }
"""

# ---------- Settings helper ----------
def app_settings():
    # QSettings will store in platform-appropriate place
    return QtCore.QSettings("SensorLabCo", "SensorLabApp")

# ---------- Splash screen ----------
class SplashScreen(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label = QtWidgets.QLabel("SENSORLAB")
        label.setStyleSheet("font-size:42px; font-weight:900; color:white;")
        sub = QtWidgets.QLabel("Multi-channel Material Sensor Interface")
        sub.setStyleSheet("color:gray; font-size:14px;")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0,100); self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedWidth(300)
        layout.addWidget(label)
        layout.addWidget(sub)
        layout.addSpacing(40)
        layout.addWidget(self.progress)
        self.timer = QtCore.QTimer(); self.timer.timeout.connect(self.step)
        self.timer.start(30)
        self.value = 0

    def step(self):
        self.value += 2
        self.progress.setValue(self.value)
        if self.value >= 100:
            self.timer.stop()
            self.close()

# ---------- Settings Dialog ----------
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(700, 480)
        self._qs = app_settings()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget()
        layout.addWidget(tabs)

        # General tab
        g = QtWidgets.QWidget(); gl = QtWidgets.QFormLayout(g)
        self.theme_combo = QtWidgets.QComboBox(); self.theme_combo.addItems(["Dark", "Light"])
        self.autostart_chk = QtWidgets.QCheckBox("Show splash on startup")
        gl.addRow("Theme", self.theme_combo)
        gl.addRow(self.autostart_chk)
        tabs.addTab(g, "General")

        # Device tab
        d = QtWidgets.QWidget(); dl = QtWidgets.QFormLayout(d)
        self.baud_combo = QtWidgets.QComboBox(); self.baud_combo.addItems(["9600","19200","38400","57600","115200"])
        self.frame_combo = QtWidgets.QComboBox(); self.frame_combo.addItems(["ASCII (CSV)","Binary"])
        self.channels_combo = QtWidgets.QComboBox(); self.channels_combo.addItems(["4","8"])
        dl.addRow("Baud rate", self.baud_combo)
        dl.addRow("Frame type", self.frame_combo)
        dl.addRow("Channels", self.channels_combo)
        tabs.addTab(d, "Device")

        # Sampling tab
        s = QtWidgets.QWidget(); sl = QtWidgets.QFormLayout(s)
        self.default_rate = QtWidgets.QSpinBox(); self.default_rate.setRange(1,200); self.default_rate.setValue(10)
        self.buffer_spin = QtWidgets.QSpinBox(); self.buffer_spin.setRange(50,5000); self.buffer_spin.setValue(300)
        self.ts_format = QtWidgets.QComboBox(); self.ts_format.addItems(["Epoch ms","ISO 8601"])
        sl.addRow("Default sampling rate (Hz)", self.default_rate)
        sl.addRow("Plot buffer size (points)", self.buffer_spin)
        sl.addRow("Timestamp format", self.ts_format)
        tabs.addTab(s, "Acquisition")

        # Heater tab
        h = QtWidgets.QWidget(); hl = QtWidgets.QFormLayout(h)
        self.heater_profile = QtWidgets.QComboBox(); self.heater_profile.addItems(["Samio","Linear","Custom"])
        self.heater_max = QtWidgets.QDoubleSpinBox(); self.heater_max.setRange(0.1,20.0); self.heater_max.setValue(5.0)
        self.preheat_spin = QtWidgets.QSpinBox(); self.preheat_spin.setRange(0,600); self.preheat_spin.setValue(30)
        hl.addRow("Profile", self.heater_profile)
        hl.addRow("Max heater voltage (V)", self.heater_max)
        hl.addRow("Preheat duration (s)", self.preheat_spin)
        tabs.addTab(h, "Heater")

        # Logging tab
        lg = QtWidgets.QWidget(); lgl = QtWidgets.QFormLayout(lg)
        self.save_format = QtWidgets.QComboBox(); self.save_format.addItems(["CSV","HDF5"])
        self.default_path = QtWidgets.QLineEdit(); btn_browse = QtWidgets.QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_path)
        self.auto_log = QtWidgets.QCheckBox("Auto-log on connect")
        lgl.addRow("Default save format", self.save_format)
        row = QtWidgets.QHBoxLayout(); row.addWidget(self.default_path); row.addWidget(btn_browse)
        lgl.addRow("Default save directory", row)
        lgl.addRow(self.auto_log)
        tabs.addTab(lg, "Logging")

        # Advanced
        a = QtWidgets.QWidget(); al = QtWidgets.QFormLayout(a)
        self.crc_chk = QtWidgets.QCheckBox("Enable CRC for binary frames")
        self.timeout_spin = QtWidgets.QSpinBox(); self.timeout_spin.setRange(1,5000); self.timeout_spin.setValue(1000)
        al.addRow(self.crc_chk)
        al.addRow("Serial timeout (ms)", self.timeout_spin)
        tabs.addTab(a, "Advanced")

        # Buttons
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Save | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.save_settings)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def browse_path(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select default save directory", os.path.expanduser("~"))
        if d:
            self.default_path.setText(d)

    def load_settings(self):
        # General
        theme = self._qs.value("ui/theme", "Dark")
        self.theme_combo.setCurrentText(theme)
        self.autostart_chk.setChecked(self._qs.value("ui/splash", "true") == "true")
        # Device
        self.baud_combo.setCurrentText(self._qs.value("device/baud", "115200"))
        self.frame_combo.setCurrentText(self._qs.value("device/frame", "ASCII (CSV)"))
        self.channels_combo.setCurrentText(self._qs.value("device/channels", "4"))
        # Acquisition
        self.default_rate.setValue(int(self._qs.value("acq/rate", 10)))
        self.buffer_spin.setValue(int(self._qs.value("acq/buffer", 300)))
        self.ts_format.setCurrentText(self._qs.value("acq/ts", "Epoch ms"))
        # Heater
        self.heater_profile.setCurrentText(self._qs.value("heater/profile", "Linear"))
        self.heater_max.setValue(float(self._qs.value("heater/max", 5.0)))
        self.preheat_spin.setValue(int(self._qs.value("heater/preheat", 30)))
        # Logging
        self.save_format.setCurrentText(self._qs.value("log/format", "CSV"))
        self.default_path.setText(self._qs.value("log/path", os.path.expanduser("~")))
        self.auto_log.setChecked(self._qs.value("log/auto", "false") == "true")
        # Advanced
        self.crc_chk.setChecked(self._qs.value("adv/crc", "false") == "true")
        self.timeout_spin.setValue(int(self._qs.value("adv/timeout", 1000)))

    def save_settings(self):
        # store values
        self._qs.setValue("ui/theme", self.theme_combo.currentText())
        self._qs.setValue("ui/splash", "true" if self.autostart_chk.isChecked() else "false")
        self._qs.setValue("device/baud", self.baud_combo.currentText())
        self._qs.setValue("device/frame", self.frame_combo.currentText())
        self._qs.setValue("device/channels", self.channels_combo.currentText())
        self._qs.setValue("acq/rate", int(self.default_rate.value()))
        self._qs.setValue("acq/buffer", int(self.buffer_spin.value()))
        self._qs.setValue("acq/ts", self.ts_format.currentText())
        self._qs.setValue("heater/profile", self.heater_profile.currentText())
        self._qs.setValue("heater/max", float(self.heater_max.value()))
        self._qs.setValue("heater/preheat", int(self.preheat_spin.value()))
        self._qs.setValue("log/format", self.save_format.currentText())
        self._qs.setValue("log/path", self.default_path.text())
        self._qs.setValue("log/auto", "true" if self.auto_log.isChecked() else "false")
        self._qs.setValue("adv/crc", "true" if self.crc_chk.isChecked() else "false")
        self._qs.setValue("adv/timeout", int(self.timeout_spin.value()))
        self.accept()

# ---------- Start Page ----------
class StartPage(QtWidgets.QWidget):
    start_requested = QtCore.pyqtSignal()
    settings_requested = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label = QtWidgets.QLabel("SENSORLAB")
        label.setStyleSheet("font-size:38px; font-weight:900;")
        sub = QtWidgets.QLabel("Multi-channel Material Sensor Interface")
        sub.setStyleSheet("color:gray;")
        btn_start = QtWidgets.QPushButton("START EXPERIMENT")
        btn_start.setObjectName("primary")
        btn_start.setFixedSize(260,50)
        btn_start.clicked.connect(self.start_requested.emit)
        btn_settings = QtWidgets.QPushButton("Settings"); btn_settings.setFixedSize(140,36)
        btn_settings.clicked.connect(self.settings_requested.emit)
        layout.addWidget(label); layout.addWidget(sub); layout.addSpacing(30)
        layout.addWidget(btn_start); layout.addSpacing(8); layout.addWidget(btn_settings)

# ---------- Main Dashboard ----------
class MainDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._qs = app_settings()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)

        # Left Control Panel
        left = QtWidgets.QFrame()
        left.setObjectName("control_panel")
        left.setFixedWidth(250)
        l = QtWidgets.QVBoxLayout(left)
        l.addWidget(QtWidgets.QLabel("Control Panel", objectName="title"))
        self.btn_connect = QtWidgets.QPushButton("Connect Device")
        l.addWidget(self.btn_connect)
        l.addWidget(QtWidgets.QLabel("Port"))
        self.port = QtWidgets.QComboBox(); self.port.addItem("Auto detect")
        l.addWidget(self.port)
        l.addWidget(QtWidgets.QLabel("Sampling Rate"))
        self.rate = QtWidgets.QSpinBox(); self.rate.setRange(1,200); self.rate.setValue(10)
        l.addWidget(self.rate)
        l.addWidget(QtWidgets.QLabel("Duration"))
        self.duration = QtWidgets.QComboBox(); self.duration.addItems(["∞","30s","1m","5m","10m"])
        l.addWidget(self.duration)
        l.addWidget(QtWidgets.QLabel("Microheater"))
        self.heat = QtWidgets.QComboBox(); self.heat.addItems(["Samio","Linear","Custom"])
        l.addWidget(self.heat)
        l.addStretch(1)
        self.save_btn = QtWidgets.QPushButton("Save Data")
        l.addWidget(self.save_btn)

        # Center plot
        center = QtWidgets.QFrame()
        c = QtWidgets.QVBoxLayout(center)
        self.plot = pg.PlotWidget(title="Live Sensor Data")
        self.plot.showGrid(x=True,y=True)
        self.plot.addLegend()
        c.addWidget(self.plot)

        # Create curves placeholder
        self.curves = []
        colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f']
        for i in range(8):
            curve = self.plot.plot([], [], pen=pg.mkPen(colors[i], width=2), name=f"CH{i+1}")
            self.curves.append(curve)

        # Right metadata panel
        right = QtWidgets.QFrame(); right.setObjectName("meta_panel"); right.setFixedWidth(260)
        r = QtWidgets.QVBoxLayout(right)
        r.addWidget(QtWidgets.QLabel("Metadata", objectName="title"))
        self.sample_id = QtWidgets.QLineEdit(); self.operator = QtWidgets.QLineEdit(); self.notes = QtWidgets.QTextEdit()
        r.addWidget(QtWidgets.QLabel("Sample ID")); r.addWidget(self.sample_id)
        r.addWidget(QtWidgets.QLabel("Operator")); r.addWidget(self.operator)
        r.addWidget(QtWidgets.QLabel("Notes")); r.addWidget(self.notes)
        self.log = QtWidgets.QCheckBox("Logging ON"); self.log.setChecked(True)
        r.addWidget(self.log); r.addStretch(1)

        layout.addWidget(left)
        layout.addWidget(center, 1)
        layout.addWidget(right)

        # plotting timer
        self.t = 0.0
        self.timer = QtCore.QTimer(); self.timer.timeout.connect(self.update_plot)
        self.timer.start(int(1000 / max(1, int(self.rate.value()))))

        # wire some controls
        self.rate.valueChanged.connect(self.on_rate_change)
        self.save_btn.clicked.connect(self.fake_save)

    def load_settings(self):
        # apply persisted defaults where sensible
        try:
            rate = int(self._qs.value("acq/rate", 10))
            self.rate.setValue(rate)
            buf = int(self._qs.value("acq/buffer", 300))
            # NOTE: buffer used when implementing real plotting logic
            channels = int(self._qs.value("device/channels", 4))
            # shrink visible curves if channels==4
            for i, c in enumerate(self.curves):
                c.setVisible(i < channels)
            # heater profile
            profile = self._qs.value("heater/profile", "Linear")
            idx = self.heat.findText(profile)
            if idx >= 0: self.heat.setCurrentIndex(idx)
        except Exception:
            pass

    def on_rate_change(self, v):
        # adjust timer interval
        if v <= 0: v = 1
        self.timer.setInterval(int(1000 / v))

    def update_plot(self):
        # simulated data
        self.t += 0.1
        for i, curve in enumerate(self.curves):
            x, y = curve.getData()
            x = x.tolist() if x is not None else []
            y = y.tolist() if y is not None else []
            if len(x) > 500: x, y = x[-500:], y[-500:]
            x.append(self.t)
            y.append(math.sin(self.t*(0.25 + i*0.06)) + i*0.2)
            curve.setData(x, y)

    def fake_save(self):
        # save to CSV or HDF5 per settings (demo CSV only)
        fmt = self._qs.value("log/format", "CSV")
        default_dir = self._qs.value("log/path", os.path.expanduser("~"))
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save data", os.path.join(default_dir, "sensor_run.csv"), "CSV Files (*.csv);;All Files (*)")
        if not fname: return
        # write demo CSV
        with open(fname, 'w') as f:
            f.write("# SensorLab demo export\n")
            f.write(f"# Sample: {self.sample_id.text()}\n")
            f.write("ts,ch1,ch2,ch3,ch4,ch5,ch6,ch7,ch8\n")
            for i in range(300):
                t = i * 0.1
                vals = [math.sin(t*0.5 + c*0.3) + c*0.1 for c in range(8)]
                line = ",".join([f"{t:.3f}"] + [f"{v:.6f}" for v in vals])
                f.write(line + "\n")
        QtWidgets.QMessageBox.information(self, "Saved", f"Saved demo CSV to:\n{fname}")

# ---------- Main Window ----------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._qs = app_settings()
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 760)
        self.stack = QtWidgets.QStackedWidget()
        self.start = StartPage()
        self.dashboard = MainDashboard()
        self.stack.addWidget(self.start)
        self.stack.addWidget(self.dashboard)
        self.setCentralWidget(self.stack)

        # menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        dev_menu = menubar.addMenu("Device")
        view_menu = menubar.addMenu("View")
        help_menu = menubar.addMenu("Help")
        # settings
        action_settings = QtGui.QAction("Settings", self)
        action_settings.triggered.connect(self.open_settings)
        file_menu.addAction(action_settings)
        # theme toggle
        act_theme = QtGui.QAction("Toggle Light/Dark", self)
        act_theme.triggered.connect(self.toggle_theme)
        view_menu.addAction(act_theme)

        # statusbar
        self.status = QtWidgets.QStatusBar(); self.setStatusBar(self.status)
        self.status.showMessage("Ready")
        self.status_left = QtWidgets.QLabel("00:00:00"); self.status.addPermanentWidget(self.status_left)
        self.status_mid = QtWidgets.QLabel("10 Hz"); self.status.addPermanentWidget(self.status_mid)
        self.status_right = QtWidgets.QLabel("Logging ON"); self.status.addPermanentWidget(self.status_right)

        # wiring
        self.start.start_requested.connect(lambda: self.stack.setCurrentWidget(self.dashboard))
        self.start.settings_requested.connect(self.open_settings)

        # apply settings (theme)
        self.apply_theme_from_settings()

        # show splash if enabled
        if self._qs.value("ui/splash", "true") == "true":
            splash = SplashScreen(self)
            splash.show()
            QtCore.QTimer.singleShot(1200, splash.close)
            QtCore.QTimer.singleShot(1200, lambda: self.stack.setCurrentWidget(self.start))
        else:
            self.stack.setCurrentWidget(self.start)

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec():  # saved
            # reapply theme and some important settings to dashboard
            self.apply_theme_from_settings()
            self.dashboard.load_settings()

    def apply_theme_from_settings(self):
        theme = self._qs.value("ui/theme", "Dark")
        if theme == "Light":
            self.setStyleSheet(LIGHT_STYLE)
        else:
            self.setStyleSheet(DARK_STYLE)

    def toggle_theme(self):
        # toggle and persist
        cur = self._qs.value("ui/theme", "Dark")
        new = "Light" if cur == "Dark" else "Dark"
        self._qs.setValue("ui/theme", new)
        self.apply_theme_from_settings()

# ---------- Run ----------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
