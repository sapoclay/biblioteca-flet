import os
import subprocess
import sys

# Nombre del entorno virtual
VENV_DIR = "venv"

# Determinar el ejecutable de Python dentro del entorno virtual
def obtener_python_ejecutable():
    if os.name == 'nt':  # Windows
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:  # Linux/macOS
        return os.path.join(VENV_DIR, "bin", "python")

# Comprobar si el entorno virtual está creado
def entorno_virtual_existe():
    return os.path.isdir(VENV_DIR)

# Crear el entorno virtual
def crear_entorno_virtual():
    print("Creando el entorno virtual...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)

# Instalar pip si no está instalado
def asegurar_pip(python_executable):
    try:
        subprocess.run([python_executable, "-m", "pip", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("pip no está instalado. Intentando instalar pip manualmente...")
        try:
            # Descargar get-pip.py
            subprocess.run([sys.executable, "-c", "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"], check=True)
            # Instalar pip usando get-pip.py
            subprocess.run([python_executable, "get-pip.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error al instalar pip manualmente: {e}")
            raise

# Instalar las dependencias desde requirements.txt
def instalar_dependencias(python_executable):
    print("Instalando dependencias...")
    asegurar_pip(python_executable)
    subprocess.run([python_executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

# Comprobar si flet está instalado en el entorno virtual
def flet_instalado(python_executable):
    try:
        result = subprocess.run(
            [python_executable, "-m", "pip", "show", "flet"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return "Name: flet" in result.stdout
    except FileNotFoundError:
        print(f"Archivo no encontrado: {python_executable}")
        return False
    except subprocess.CalledProcessError:
        return False

# Mostrar mensajes usando Flet si está instalado
def mostrar_mensaje(mensaje):
    python_executable = obtener_python_ejecutable()
    
    if flet_instalado(python_executable):
        try:
            import flet as ft
            def main(page: ft.Page):
                page.add(ft.Text(mensaje))
                page.update()
            ft.app(target=main)
        except ImportError:
            print("Error al importar Flet.")
    else:
        print(mensaje)

# Ejecutar el script principal dentro del entorno virtual
def ejecutar_app():
    python_executable = obtener_python_ejecutable()
    if os.path.isfile(python_executable):
        subprocess.run([python_executable, "main.py"], check=True)
    else:
        print(f"El ejecutable no se encuentra: {python_executable}")

# Lógica principal
def main():
    if not entorno_virtual_existe():
        # Si no existe el entorno virtual, crearlo e instalar dependencias
        print("El entorno virtual no existe. Creando uno nuevo...")
        crear_entorno_virtual()
        python_executable = obtener_python_ejecutable()
        instalar_dependencias(python_executable)
    else:
        # Si el entorno virtual ya existe
        print("El entorno virtual ya existe.")
        python_executable = obtener_python_ejecutable()

        # Instalar dependencias si no lo hicimos aún y no tenemos flet
        if not flet_instalado(python_executable):
            print("Flet no está instalado. Instalando Flet...")
            asegurar_pip(python_executable)  # Asegura que pip esté disponible
            subprocess.run([python_executable, "-m", "pip", "install", "flet"], check=True)
            print("Flet instalado correctamente.")
    
    # Ejecutar la aplicación
    ejecutar_app()

# Ejecutar el script
if __name__ == "__main__":
    main()
