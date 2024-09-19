import flet as ft
import sqlite3
from pathlib import Path
from database import (crear_tablas, guardar_libro, guardar_favorito, 
                      get_categorias_from_db, guardar_cambios_libro, cargar_datos,
                      actualizar_categoria_libro_individual, agregar_categoria, eliminar_libro,
                      conectar_db)
from models import Libro
from utils import (actualizar_lista_libros, mostrar_mensaje_error, 
                   abrir_libro, buscar_libro, cerrar_dialogo, aplicar_categoria_a_libros,
                   handle_window_event, create_confirm_dialog, salir_app, aplicar_categoria_a_libros_con_confirmacion,
                   mostrar_about_dialog)
from themes import toggle_tema
from dialog import (mostrar_dialogo_nuevo_libro, mostrar_dialogo_seleccionar_categoria, 
                    manejar_cambio_categoria, procesar_archivo_dialog, mostrar_dialogo_url)

# Aplicación de Biblioteca Digital
def main(page: ft.Page):
    # Ruta a la base de datos SQLite
    DB_FILE = "libros.db"

    # Conexión a la base de datos SQLite
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Crear tablas si no existen
    crear_tablas()

    # Lista para almacenar los libros y favoritos
    libros = []
    favoritos = []

    cargar_datos(libros, favoritos)
    
    mostrar_favoritos = False
    tema_oscuro = False
    # Establecer tema inicial (oscuro)
    page.theme_mode = ft.ThemeMode.DARK
    
    # Función para alternar entre tema claro y oscuro
    def alternar_tema(e):
        nonlocal tema_oscuro
        tema_oscuro = toggle_tema(page, tema_oscuro)
    
    # Función para guardar el nuevo libro
    def guardar_nuevo_libro(titulo, categoria, ruta):
        nuevo_libro = Libro(titulo, categoria, ruta)
        
        # Añadir log para ver el libro que se intenta guardar
        print(f"Guardando libro: Título: {titulo}, Categoría: {categoria}, Ruta: {ruta}")
        
        # Guardar en la base de datos
        try:
            guardar_libro(nuevo_libro)  # Asegúrate de que el método `guardar_libro` funcione correctamente en la base de datos
            
            # Añadir el libro a la lista en memoria
            libros.append(nuevo_libro)
            
            # Actualizar la lista de libros en la interfaz
            actualizar_lista_libros(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro)
            page.update()

        except Exception as e:
            print(f"Error al guardar libro en la base de datos: {e}")


    # Función para añadir o quitar de favoritos
    def toggle_favorito(libro):
        if libro in favoritos:
            favoritos.remove(libro)
            guardar_favorito(libro)
        else:
            favoritos.append(libro)
            guardar_favorito(libro)
        actualizar_lista_libros(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro)

    def eliminar_libro_click_event(e, libro):
        # Conectar a la base de datos
        conexion = conectar_db()
        cursor = conexion.cursor()

        # Llamar a la función eliminar_libro de archivo database
        eliminar_libro(
            libro, 
            cursor, 
            conexion, 
            page, 
            lista_libros, 
            libros, 
            favoritos, 
            mostrar_favoritos, 
            abrir_libro, 
            toggle_favorito, 
            eliminar_libro_click_event,  # Cambia esto a eliminar_libro si se refiere a la función en database.py
            editar_libro
        )

        # Cerrar la conexión después de la llamada
        conexion.close()
    
    # Función para editar un libro
    def editar_libro(libro):
        categorias = get_categorias_from_db() + ["Nueva categoría..."]
        categoria_field = ft.Dropdown(
            label="Categoría del libro",
            value=libro.categoria,
            options=[ft.dropdown.Option(text=categoria) for categoria in categorias]
        )
        categoria_field.on_change = lambda e: manejar_cambio_categoria(categoria_field, libro.ruta, page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro, cursor, conn)
        titulo_field = ft.TextField(label="Título del libro", value=libro.titulo)
        ruta_field = ft.TextField(label="Ruta del archivo", value=libro.ruta, disabled=True)
        guardar_btn = ft.ElevatedButton(
                    text="Guardar cambios", 
                    on_click=lambda _: guardar_cambios_libro(
                        page, libro, titulo_field.value, categoria_field.value,
                        lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro
                    )
                )
        dialogo_editar = ft.AlertDialog(title=ft.Text("Editar libro"), content=ft.Column([titulo_field, categoria_field, ruta_field, guardar_btn]))
        page.overlay.append(dialogo_editar)
        dialogo_editar.open = True
        page.update()

    # Función para mostrar solo los libros favoritos
    def mostrar_solo_favoritos(e):
        nonlocal mostrar_favoritos
        mostrar_favoritos = not mostrar_favoritos
        actualizar_lista_libros(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro)

    # Función para procesar los archivos seleccionados
    def procesar_archivo(e: ft.FilePickerResultEvent):
        if e.files:  # Verifica si se seleccionaron archivos
            for archivo in e.files:
                ruta = archivo.path
                if ruta.lower().endswith('.pdf'):
                    titulo = Path(ruta).stem
                    mostrar_dialogo_nuevo_libro(page, titulo, ruta, "", guardar_nuevo_libro)
        else:
            print("No se seleccionaron archivos")
    
    def procesar_carpeta(e: ft.FilePickerResultEvent):
        if e.path:
            carpeta = Path(e.path)
            print(f"Ruta obtenida del selector de archivos: '{carpeta}'")
            categorias_disponibles = ["Documentación", "Documentación oficial", "Manual", "Tecnología", "Ciencia", "Filosofía", "Historia"]
            aplicar_categoria_a_libros_con_confirmacion(
                page,
                carpeta,
                libros,
                lista_libros,
                favoritos,
                mostrar_favoritos,
                abrir_libro,
                toggle_favorito,
                eliminar_libro,
                editar_libro,
                categorias_disponibles
            )

    # Crear un FilePicker para seleccionar archivos
    archivo_pdf = ft.FilePicker(on_result=procesar_archivo)
    page.overlay.append(archivo_pdf)

    # Crear un FilePicker para seleccionar una carpeta
    file_picker_carpeta = ft.FilePicker(on_result=procesar_carpeta)
    page.overlay.append(file_picker_carpeta)

    # Función para cargar libros desde una carpeta
    def cargar_libros_carpeta(e):
        # Abre el diálogo para seleccionar una carpeta
        file_picker_carpeta.get_directory_path()

    # Elementos de la interfaz
    barra_busqueda = ft.TextField(
        label="Buscar libro (Título o Categoría)...",
        on_change=lambda e: buscar_libro(page, lista_libros, libros, favoritos, mostrar_favoritos, e.control.value, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro)
    )    
    lista_libros = ft.Column()  # Usamos Column aquí
    boton_cargar = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=lambda _: archivo_pdf.pick_files(), tooltip="Añadir nuevo libro")
    boton_cargar_carpeta = ft.FloatingActionButton(icon=ft.icons.FOLDER, on_click=cargar_libros_carpeta, tooltip="Cargar libros desde carpeta")
    btn_add_url = ft.FloatingActionButton(
        icon=ft.icons.ADD_LINK,
        on_click=lambda e: mostrar_dialogo_url(
            page,
            lista_libros,                 
            libros,                       
            favoritos,                    
            mostrar_favoritos,            
            abrir_libro,                  
            toggle_favorito,              
            eliminar_libro_click_event,   
            editar_libro                  
        ),
        tooltip="Cargar libros desde URL"
    )    
    boton_favoritos = ft.IconButton(icon=ft.icons.STAR, on_click=mostrar_solo_favoritos, selected_icon=ft.icons.STAR_BORDER, tooltip="Mostrar solo favoritos")
    boton_tema = ft.IconButton(icon=ft.icons.DARK_MODE, on_click=alternar_tema, tooltip="Alternar tema claro/oscuro")
    
    # Crear el menú
    menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(text="Acerca de", on_click=lambda e: mostrar_about_dialog(e, page)),
            ft.PopupMenuItem(text="Salir", on_click=lambda _: salir_app(page))
        ]
    )

    # Crear un diálogo de confirmación para manejar el cierre
    def on_confirm_exit():
        page.window.destroy()

    # Aquí pasamos los argumentos correctos
    confirm_dialog = create_confirm_dialog(page, on_confirm_exit)

    # Prevenir el cierre automático y manejar el evento de cierre
    page.window.prevent_close = True
    page.window.on_event = handle_window_event(page, confirm_dialog)

    # Estructura de la página
    page.appbar = ft.AppBar(
        title=ft.Text("Biblioteca Digital"),
        actions=[menu]
    )
    
    # Crear encabezados con espacio adicional
    encabezados = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text("Libros", size=16, weight=ft.FontWeight.BOLD),
                padding=ft.Padding(left=20, top=0, right=0, bottom=0),  # Agregar padding completo
                alignment=ft.alignment.center_left,
                expand=True
            ),
            ft.Container(
                content=ft.Text("Categorías", size=16, weight=ft.FontWeight.BOLD),
                alignment=ft.alignment.center,
                expand=True
            ),
            ft.Container(
                content=ft.Text("Acciones", size=16, weight=ft.FontWeight.BOLD),
                padding=ft.Padding(left=0, top=0, right=30, bottom=0),  # Agregar padding completo
                alignment=ft.alignment.center_right,
                expand=True
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Espacio entre controles
        expand=True
    )
    
    # Estructura de la página
    page.add(
        ft.Row([barra_busqueda, boton_favoritos, boton_tema]),
        ft.Divider(),
        ft.Column(
            controls=[
                encabezados,
                ft.Container(
                    content=lista_libros,
                    expand=True
                )
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,  # Permite el desplazamiento vertical
        ),
        ft.Row([boton_cargar, boton_cargar_carpeta, btn_add_url], alignment=ft.MainAxisAlignment.END)
    )
    
    # Actualizar la lista de libros en la interfaz al iniciar
    actualizar_lista_libros(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro)
    # Cerrar la conexión al cerrar la aplicación
    page.on_close = lambda e: conn.close()

# Ejecutar la aplicación Flet
ft.app(target=main)
