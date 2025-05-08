import os
import subprocess
import sys

REQ_FILE = "requirements.txt"

def main():
    if os.path.exists(REQ_FILE):
        print(f"📦 Instalacja zależności z pliku {REQ_FILE}...\n")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQ_FILE])
        print("\n✅ Zakończono instalację.")
    else:
        print(f"⚠️  Plik {REQ_FILE} nie został znaleziony w katalogu: {os.getcwd()}")

if __name__ == "__main__":
    main()
