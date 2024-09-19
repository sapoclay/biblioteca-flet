import sys
import pystray
from pystray import MenuItem, Icon
from PIL import Image
from utils import mostrar_about_dialog

# Función para salir del programa
def salir_icono(icon, item):
    icon.stop()
    sys.exit()

# Función para crear el icono de la bandeja
def crear_icono(page):
    # Cargar la imagen del icono
    icono = Image.open("resources/Biblioteca.ico")
    
    # Función para mostrar el diálogo "Acerca de"
    def mostrar_about_icono(icon, item):
        mostrar_about_dialog(page)

    # Función para restaurar la ventana
    def restaurar_icono(icon, item):
        page.window.restore()  # Restaura la ventana

    # Crear el menú
    menu = (MenuItem("Acerca de", mostrar_about_icono),
            MenuItem("Restaurar", restaurar_icono),
            MenuItem("Salir", salir_icono))
    
    # Crear el icono
    icon = Icon("Biblioteca", icono, "Biblioteca Digital", menu)
    icon.run()