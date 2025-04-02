import sys
import psutil
import subprocess
import random
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPalette
import pyqtgraph as pg

class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Birdwatch - System Monitor")
        self.setGeometry(90, 100, 1000, 700) #changed from 100, 100, 1000, 700, to 50 starting 
        self.setup_ui()
        self.set_dark_mode()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(3000)

        # Start tshark packet capture in background thread
        self.capture_thread = threading.Thread(target=self.run_tshark_stream, daemon=True)
        self.capture_thread.start()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.header = QLabel(" BIRDWATCH REAL-TIME TRAFFIC ANALYSIS")
        self.header.setFont(QFont("Consolas", 18, QFont.Bold))
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("color: #00FFD1;")
        layout.addWidget(self.header)

        # === Traffic Chart and Protocol Stats ===
        chart_layout = QHBoxLayout()

        self.traffic_plot = pg.PlotWidget(title="Traffic")
        self.traffic_plot.setBackground("#1e1e1e")
        self.traffic_plot.showGrid(x=True, y=True)
        self.traffic_plot.setLabel('left', 'kB/s')
        self.traffic_plot.setLabel('bottom', 'Time')
        self.traffic_data = [0] * 50
        self.traffic_curve = self.traffic_plot.plot(self.traffic_data, pen=pg.mkPen('#00FFC6', width=2))
        chart_layout.addWidget(self.traffic_plot)

        self.protocol_stats = QLabel("Protocol Hierarchy (Mock)\n\nTCP: 60%\nTLS: 20%\nDNS: 15%\nICMP: 5%")
        self.protocol_stats.setStyleSheet("color: white; font: 14px monospace;")
        chart_layout.addWidget(self.protocol_stats)

        layout.addLayout(chart_layout)

        # === Filter Bar ===
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter: e.g. tcp.port == 80")
        filter_layout.addWidget(self.filter_input)

        self.apply_button = QPushButton("Apply Filter")
        self.apply_button.setStyleSheet("background-color: #00bfa5; color: white; padding: 6px;")
        filter_layout.addWidget(self.apply_button)
        layout.addLayout(filter_layout)

        # === Stats Output ===
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setFont(QFont("Courier", 11))
        self.stats_display.setStyleSheet("background-color: #1e1e1e; color: #00FF00; padding: 10px;")
        layout.addWidget(self.stats_display)

        # === Table ===
        self.packet_table = QTableWidget(0, 6)
        self.packet_table.setHorizontalHeaderLabels(["No.", "Time", "Source", "Destination", "Protocol", "Info"])
        layout.addWidget(self.packet_table)

        # === Buttons ===
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton("🧹 Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet("background-color: #007ACC; color: white; padding: 8px; border-radius: 5px;")
        button_layout.addWidget(self.clear_button)

        self.refresh_button = QPushButton("Refresh Now")
        self.refresh_button.clicked.connect(self.update_stats)
        self.refresh_button.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; border-radius: 5px;")
        button_layout.addWidget(self.refresh_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def set_dark_mode(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#121212"))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor("#1e1e1e"))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor("#2d2d30"))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor("#00FFCC"))
        self.setPalette(palette)

    def update_stats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        try:
            netstat = subprocess.run(["netstat", "-tunapl"], capture_output=True, text=True).stdout
        except Exception as e:
            netstat = f"Error getting connections: {e}"

        log = f" CPU Usage: {cpu}%\n RAM Usage: {ram}%\n\n Active Connections:\n{netstat}"
        self.stats_display.setText(log)

        # update traffic graph with mock data
        new_val = random.randint(50, 250)
        self.traffic_data = self.traffic_data[1:] + [new_val]
        self.traffic_curve.setData(self.traffic_data)

    def clear_logs(self):
        self.stats_display.clear()
        self.packet_table.setRowCount(0)

    def run_tshark_stream(self):
        cmd = [
            "tshark",
            "-i", "any",
            "-T", "fields",
            "-e", "frame.number",
            "-e", "frame.time_relative",
            "-e", "ip.src",
            "-e", "ip.dst",
            "-e", "_ws.col.Protocol",
            "-e", "_ws.col.Info",
            "-l"
        ]
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            for line in process.stdout:
                fields = line.strip().split('\t')
                if len(fields) < 6:
                    continue
                self.add_packet_row(fields)
        except Exception as e:
            print(f"Error starting tshark: {e}")

    def add_packet_row(self, row_data):
        def update_ui():
            row = self.packet_table.rowCount()
            self.packet_table.insertRow(row)
            for col, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                self.packet_table.setItem(row, col, item)

            if self.packet_table.rowCount() > 100:
                self.packet_table.removeRow(0)

        QTimer.singleShot(0, update_ui)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec_())
