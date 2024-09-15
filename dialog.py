import flet as ft
from utils import cerrar_dialogo, aplicar_categoria_a_libros
from database import get_categorias_from_db, agregar_categoria, actualizar_categoria_libro_individual,conectar_db,añadir_pdf_desde_url
import os

def mostrar_dialogo_nuevo_libro(page: ft.Page, titulo: str, ruta: str, categoria: str, guardar_nuevo_libro):
    # Crear un título que muestre el nombre del libro
    titulo_texto = ft.Text(f"Título: {titulo}", size=18, weight="bold")
    
    # Crear un texto que muestre la ruta del archivo
    ruta_texto = ft.Text(f"Ruta: {ruta}", size=14, italic=True)
    
    # Botón de guardar
    guardar_btn = ft.ElevatedButton(
        text="Guardar", 
        on_click=lambda _: guardar_nuevo_libro(titulo, categoria, ruta),
        width=200  # Ancho del botón
    )
    
    # Botón de cancelar
    cancelar_btn = ft.ElevatedButton(
        text="Cancelar",
        on_click=lambda _: cerrar_dialogo(page),
        width=200  # Ancho del botón
    )
    
    # Contenedor para los botones
    botones_container = ft.Row([guardar_btn, cancelar_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    
    # Contenedor para el contenido del diálogo
    content_container = ft.Container(
        content=ft.Column([titulo_texto, ruta_texto, botones_container], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
        width=400,  # Ancho del contenedor ajustado para acomodar la información
        height=250,  # Alto del contenedor ajustado para incluir la ruta
        alignment=ft.alignment.center,  # Centra el contenido dentro del contenedor
    )
    
    # Crear el diálogo
    dialogo_agregar = ft.AlertDialog(
        title=ft.Text("Agregar nuevo libro"),
        content=content_container,
        modal=True,
    )
       
    # Añadir el diálogo a la página y mostrarlo
    page.overlay.append(dialogo_agregar)
    dialogo_agregar.open = True
    page.update()



def mostrar_dialogo_seleccionar_categoria(page, carpeta, libros, lista_libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro):
    # Crear la conexión y obtener el cursor
    conn = conectar_db()
    cursor = conn.cursor()

    # Obtener las categorías disponibles
    categorias = get_categorias_from_db() + ["Nueva categoría..."]

    # Crear el dropdown para seleccionar la categoría
    categoria_field = ft.Dropdown(
        label="Categoría para todos los libros",
        options=[ft.dropdown.Option(text=categoria) for categoria in categorias],
        value=categorias[0]
    )

    # Configurar el evento on_change para manejar el cambio de categoría
    categoria_field.on_change = lambda e: manejar_cambio_categoria(
        categoria_field, carpeta, page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro, cursor, conn
    )

    # Botón para aplicar el cambio de categoría
    guardar_btn = ft.ElevatedButton(
        text="Aplicar categoría", 
        on_click=lambda _: manejar_cambio_categoria(
            categoria_field, carpeta, page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro, cursor, conn
        )
    )

    # Crear el diálogo con el dropdown y el botón
    dialogo_categoria = ft.AlertDialog(
        title=ft.Text("Seleccionar categoría"),
        content=ft.Column([categoria_field, guardar_btn])
    )

    # Mostrar el diálogo
    page.overlay.append(dialogo_categoria)
    dialogo_categoria.open = True
    page.update()


def manejar_cambio_categoria(categoria_field, ruta, page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro, cursor, conn):
    categoria = categoria_field.value

    if categoria == "Nueva categoría...":
        mostrar_dialogo_nueva_categoria(
            ruta,            # La ruta de la carpeta o archivo
            libros,          # Lista de libros
            page,            # Página de la aplicación
            lista_libros,    # Lista visual de los libros
            favoritos,       # Libros favoritos
            mostrar_favoritos, # Función para mostrar favoritos
            abrir_libro,     # Función para abrir un libro
            toggle_favorito, # Función para marcar/desmarcar favoritos
            eliminar_libro,  # Función para eliminar un libro
            editar_libro     # Función para editar un libro
        )
    else:
        # Verifica si la ruta es un directorio o un archivo
        if os.path.isdir(ruta):
            # Si es un directorio, aplicar la categoría a todos los libros en la carpeta
            aplicar_categoria_a_libros(
                        page, categoria, ruta, libros, lista_libros, favoritos, mostrar_favoritos, abrir_libro, 
                        toggle_favorito, eliminar_libro, editar_libro
                    )
        else:
            # Si es un archivo, actualizar solo ese libro
            actualizar_categoria_libro_individual(
                libros, ruta, categoria, cursor, conn, 
                page, lista_libros, favoritos, mostrar_favoritos, 
                abrir_libro, toggle_favorito, eliminar_libro, editar_libro
            )

def mostrar_dialogo_nueva_categoria(
    carpeta, libros, page, lista_libros, favoritos, mostrar_favoritos,
    abrir_libro, toggle_favorito, eliminar_libro, editar_libro
):
    """
    Muestra el diálogo para agregar una nueva categoría y actualiza la base de datos.
    """

    # Campo de texto para ingresar el nombre de la nueva categoría
    nueva_categoria_dialogo = ft.TextField(
        label="Nombre de la nueva categoría",
        on_change=lambda e: e.control.value
    )

    # Botón para agregar la nueva categoría
    guardar_btn = ft.ElevatedButton(
        text="Agregar",
        on_click=lambda _: agregar_categoria(
            nueva_categoria_dialogo.value,  # La nueva categoría ingresada
            carpeta,                        # La carpeta o ruta seleccionada
            libros,                         # Lista de libros
            page,                           # Página de la aplicación
            lista_libros,                   # Lista visual de los libros
            favoritos,                      # Libros favoritos
            mostrar_favoritos,              # Función para mostrar favoritos
            abrir_libro,                    # Función para abrir un libro
            toggle_favorito,                # Función para marcar/desmarcar favoritos
            eliminar_libro,                 # Función para eliminar un libro
            editar_libro                    # Función para editar un libro
        )
    )

    # Creación del diálogo para agregar una nueva categoría
    dialogo_nueva_categoria = ft.AlertDialog(
        title=ft.Text("Nueva categoría"),
        content=ft.Column([nueva_categoria_dialogo, guardar_btn])
    )

    # Añadir el diálogo a la página y mostrarlo
    page.overlay.append(dialogo_nueva_categoria)
    dialogo_nueva_categoria.open = True
    page.update()
    
def procesar_archivo_dialog(e, page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro):
    from pathlib import Path
    from main import guardar_nuevo_libro
    for archivo in e.files:
        ruta = archivo.path
        if ruta.lower().endswith('.pdf'):
            titulo = Path(ruta).stem
            # Llamada a la función mostrar_dialogo_nuevo_libro
            mostrar_dialogo_nuevo_libro(
                page, titulo, ruta, "", 
                lambda titulo, categoria, ruta: guardar_nuevo_libro(titulo, categoria, ruta)
            )
            
def mostrar_dialogo_url(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro):
    pdf_url_field = ft.TextField(label="URL del PDF")
    pdf_name_field = ft.TextField(label="Nombre")
    pdf_category_field = ft.TextField(label="Categoría")

    # Crear el diálogo
    dialog = ft.AlertDialog(
        title=ft.Text("Añadir PDF desde URL"),
        content=ft.Column(
            controls=[
                pdf_url_field,
                pdf_name_field,
                pdf_category_field,
                ft.ElevatedButton(
                    text="Añadir",
                    on_click=lambda e: añadir_pdf_desde_url(
                        e,
                        page,
                        pdf_url_field,
                        pdf_name_field,
                        pdf_category_field,
                        lista_libros,
                        libros,
                        favoritos,
                        mostrar_favoritos,
                        abrir_libro,
                        toggle_favorito,
                        eliminar_libro_click_event,
                        editar_libro

                    )
                ),
            ]
        ),
        actions=[
            ft.TextButton(text="Cancelar", on_click=lambda e: cerrar_dialogo(page))  # Cerrar el diálogo cuando se cancele
        ]
    )

    # Mostrar el diálogo
    page.overlay.append(dialog)
    dialog.open = True
    page.update()



