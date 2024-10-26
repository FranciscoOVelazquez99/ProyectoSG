from waitress import serve
from SGM import app
import socket

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

if __name__ == "__main__":
    host = get_ip()
    port = 5010
    print(f"Aplicación ejecutándose en http://{host}:{port}")
    serve(app, host=host, port=port)