import subprocess
import threading


class WiresharkMonitor:
    def __init__(self, interface="lo", on_packet=None):
        self.interface = interface
        self.on_packet = on_packet
        self.process = None

    def start_capture(self):
        def run_tshark():
            self.process = subprocess.Popen(
                ["tshark", "-i", self.interface, "-l"],  # -l = line-buffered
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            for line in self.process.stdout:
                if self.on_packet:
                    self.on_packet(line.strip())

        threading.Thread(target=run_tshark, daemon=True).start()

    def stop_capture(self):
        if self.process:
            self.process.terminate()
