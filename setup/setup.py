import os
import shutil
import zipfile
import urllib.request

REPO_URL = "https://github.com/pkonieczny007/PROJEKT-DODAWANIE-INFO-DO-GI-CIA/archive/refs/heads/main.zip"
ZIP_NAME = "repo.zip"
EXTRACTED_FOLDER = "PROJEKT-DODAWANIE-INFO-DO-GI-CIA-main"

def download_repo():
    print("🔽 Pobieranie repozytorium...")
    urllib.request.urlretrieve(REPO_URL, ZIP_NAME)

def unzip_repo():
    print("📦 Rozpakowywanie plików...")
    with zipfile.ZipFile(ZIP_NAME, 'r') as zip_ref:
        zip_ref.extractall(".")

def prepare_folders():
    print("📁 Tworzenie folderów Rysunki i setup...")
    os.makedirs("Rysunki", exist_ok=True)
    os.makedirs("setup", exist_ok=True)

def move_installer():
    print("📂 Przenoszenie pliku setup.py do folderu setup...")
    current_file = os.path.basename(__file__)
    shutil.copy(current_file, os.path.join("setup", current_file))

def copy_project_files():
    print("📄 Przenoszenie plików projektu do katalogu głównego...")
    for item in os.listdir(EXTRACTED_FOLDER):
        src_path = os.path.join(EXTRACTED_FOLDER, item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, item, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, ".")

def create_requirements():
    print("🧾 Tworzenie pliku requirements.txt...")
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write("pandas\nPyMuPDF\n")

def clean_up():
    print("🧹 Czyszczenie plików tymczasowych...")
    os.remove(ZIP_NAME)
    shutil.rmtree(EXTRACTED_FOLDER, ignore_errors=True)

def main():
    download_repo()
    unzip_repo()
    prepare_folders()
    copy_project_files()
    create_requirements()
    move_installer()
    clean_up()
    print("✅ Instalacja zakończona pomyślnie.")

if __name__ == "__main__":
    main()
