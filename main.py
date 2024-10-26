import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSharedMemory, Qt
from threading import Thread
from SGM import app
from waitress import serve
import socket
import win32gui
import win32con

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def run_flask():
    host = get_ip()
    port = 5010
    print(f"Aplicación ejecutándose en http://{host}:{port}")
    serve(app, host=host, port=port)

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)
        exit_action = menu.addAction("Salir")
        exit_action.triggered.connect(self.exit)
        self.setContextMenu(menu)

    def exit(self):
        QApplication.quit()

def hide_console():
    console_window = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(console_window, win32con.SW_HIDE)

if __name__ == "__main__":
    hide_console()

    shared_memory = QSharedMemory("SGwebUniqueKey")
    if shared_memory.attach():
        print("La aplicación ya está en ejecución.")
        sys.exit(0)

    if not shared_memory.create(1):
        print("No se pudo crear la memoria compartida.")
        sys.exit(1)

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)

    icon_path = os.path.join(os.path.dirname(sys.executable), "logo.ico")
    icon = QIcon(icon_path)
    tray_icon = SystemTrayIcon(icon)
    tray_icon.show()

    sys.exit(qt_app.exec_())