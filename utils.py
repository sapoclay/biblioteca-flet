import flet as ft
import os
from models import Libro
from pathlib import Path  # Importa Path desde pathlib
import webbrowser

# Función para mostrar un cuadro de diálogo con un mensaje de error
def mostrar_mensaje_error(page, mensaje):
    error_dialog = ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text(mensaje),
        actions=[
            ft.TextButton(text="OK", on_click=lambda e: error_dialog.close())
        ]
    )
    page.overlay.append(error_dialog)
    error_dialog.open()

# Actualizar la lista de libros en la interfaz
def actualizar_lista_libros(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro):
    try:
        # Limpiar los controles existentes
        lista_libros.controls.clear()
        
        # Agregar nuevos controles para cada libro
        for libro in (favoritos if mostrar_favoritos else libros):
            lista_libros.controls.append(
                ft.ListTile(
                    leading=ft.Row(
                        controls=[
                            ft.Text(libro.titulo, text_align=ft.TextAlign.START, expand=True),
                            ft.Text(libro.categoria, text_align=ft.TextAlign.START, expand=True)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    on_click=lambda e, l=libro: abrir_libro(l),
                    trailing=ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.STAR_BORDER if libro not in favoritos else ft.icons.STAR,
                                on_click=lambda e, l=libro: toggle_favorito(l),
                                tooltip="Marcar como favorito" if libro not in favoritos else "Quitar de favoritos"
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                on_click=configurar_eliminar_libro_evento(libro, eliminar_libro_click_event),
                                tooltip="Eliminar libro"
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                on_click=lambda e, l=libro: editar_libro(l),
                                tooltip="Editar libro"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                )
            )
        
        # Actualizar la página con los nuevos controles
        page.update()
    except Exception as e:
        mostrar_mensaje_error(page, f"Error al actualizar la lista de libros: {e}")


# Función para abrir el libro seleccionado
def abrir_libro(libro):
    try:
        os.startfile(libro.ruta) if os.name == 'nt' else os.system(f'open "{libro.ruta}"')
    except Exception as e:
        # Manejo de errores: mostrar el error en un cuadro de diálogo
        mostrar_mensaje_error(f"Error al abrir el archivo: {e}")


 
# Función para buscar libros (SOLO TÍTULO)       
def buscar_libro(page, lista_libros, libros, favoritos, mostrar_favoritos, texto, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro):
    try:
        texto = texto.lower()
        lista_libros.controls.clear()
        for libro in (favoritos if mostrar_favoritos else libros):
            if texto in libro.titulo.lower() or texto in libro.categoria.lower():
                lista_libros.controls.append(
                    ft.ListTile(
                        leading=ft.Row(
                            controls=[
                                ft.Text(libro.titulo, text_align=ft.TextAlign.START, expand=True),
                                ft.Text(libro.categoria, text_align=ft.TextAlign.START, expand=True)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        on_click=lambda e, l=libro: abrir_libro(l),
                        trailing=ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.STAR_BORDER if libro not in favoritos else ft.icons.STAR,
                                    on_click=lambda e, l=libro: toggle_favorito(l),
                                    tooltip="Marcar como favorito" if libro not in favoritos else "Quitar de favoritos"
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    on_click=configurar_eliminar_libro_evento(libro, eliminar_libro_click_event),
                                    tooltip="Eliminar libro"
                                ),
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    on_click=lambda e, l=libro: editar_libro(l),
                                    tooltip="Editar libro"
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END
                        )
                    )
                )
        page.update()
    except Exception as e:
        mostrar_mensaje_error(f"Error al realizar la búsqueda: {e}")
        
# Función para cerrar los cuadros de diálogo en la aplicación
def cerrar_dialogo(page):
    try:
        if page.overlay:
            page.overlay[-1].open = False
            page.update()
    except Exception as e:
        snack_bar = ft.SnackBar(ft.Text(f"Error al cerrar el cuadro de diálogo: {e}"))
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
        
def aplicar_categoria_a_libros(page, categoria, carpeta, libros, lista_libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro):
    from database import guardar_libro

    # Verificar si 'carpeta' es una lista o una cadena
    if isinstance(carpeta, list):
        # Si es una lista, iterar sobre cada ruta
        for carpeta_individual in carpeta:
            # Asegurarse de que cada elemento es una ruta de carpeta válida
            if isinstance(carpeta_individual, str) and os.path.isdir(carpeta_individual):
                for archivo in os.listdir(carpeta_individual):
                    ruta = os.path.join(carpeta_individual, archivo)
                    if os.path.isfile(ruta) and archivo.lower().endswith('.pdf'):
                        titulo = Path(ruta).stem
                        nuevo_libro = Libro(titulo, categoria, ruta)
                        libros.append(nuevo_libro)
                        guardar_libro(nuevo_libro)
    else:
        # Si es una cadena, procesar directamente
        if isinstance(carpeta, str) and os.path.isdir(carpeta):
            for archivo in os.listdir(carpeta):
                ruta = os.path.join(carpeta, archivo)
                if os.path.isfile(ruta) and archivo.lower().endswith('.pdf'):
                    titulo = Path(ruta).stem
                    nuevo_libro = Libro(titulo, categoria, ruta)
                    libros.append(nuevo_libro)
                    guardar_libro(nuevo_libro)

    # Actualizar la lista de libros en la interfaz
    actualizar_lista_libros(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro)

def configurar_eliminar_libro_evento(libro, eliminar_libro_click_event):
    return lambda e: eliminar_libro_click_event(e, libro)


def abrir_pdf(e):
    url = e.control.data
    webbrowser.open(url)
    
# Salir de la aplicación
def handle_window_event(page, confirm_dialog):
    def _handle_window_event(e):
        if e.data == "close":
            page.open(confirm_dialog)
    return _handle_window_event

def create_confirm_dialog(page, on_yes):
    def yes_click(e):
        on_yes()  # Ejecutar la acción de "Sí" proporcionada

    def no_click(e):
        page.close(confirm_dialog)  # Cerrar el diálogo de confirmación

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por favor confirma"),
        content=ft.Text("¿Estás seguro de que deseas salir de la aplicación?"),
        actions=[
            ft.ElevatedButton("Sí", on_click=yes_click),
            ft.OutlinedButton("No", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    return confirm_dialog

def salir_app(page):
    def on_exit():
        page.window.destroy()  # Cerrar la ventana de forma forzada

    confirm_dialog = create_confirm_dialog(page, on_exit)
    page.open(confirm_dialog)