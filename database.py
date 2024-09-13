import sqlite3
import os
from sqlite3 import Error
from utils import actualizar_lista_libros,cerrar_dialogo, aplicar_categoria_a_libros, mostrar_mensaje_error,abrir_pdf
from models import Libro
import flet as ft


def conectar_db():
    db_path = 'libros.db'
    if not os.path.exists(db_path):
        print(f"Creando nueva base de datos en {db_path}")
    else:
        print(f"Conectando a la base de datos en {db_path}")

    conexion = sqlite3.connect(db_path)
    return conexion

def crear_tablas():
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT,
            ruta TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favoritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER NOT NULL,
            FOREIGN KEY (libro_id) REFERENCES libros(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    conexion.commit()
    conexion.close()

def cargar_datos(libros, favoritos):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        # Cargar libros
        cursor.execute('SELECT * FROM libros')
        rows = cursor.fetchall()
        for row in rows:
            libros.append(Libro(row[1], row[2], row[3]))

        # Cargar favoritos
        cursor.execute('SELECT libro_id FROM favoritos')
        fav_rows = cursor.fetchall()
        fav_ids = [row[0] for row in fav_rows]
        for libro in libros:
            libro_id = cursor.execute('SELECT id FROM libros WHERE ruta=?', (libro.ruta,)).fetchone()[0]
            if libro_id in fav_ids:
                favoritos.append(libro)

    except Error as e:
        print(f"Error al cargar los datos: {e}")

    finally:
        if conexion:
            conexion.close()

# Guardar libro único añadido por usuario
def guardar_libro(libro):
    try:
        # Conectar a la base de datos
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        # Insertar el libro en la base de datos
        cursor.execute('INSERT INTO libros (titulo, categoria, ruta) VALUES (?, ?, ?)',
                       (libro.titulo, libro.categoria, libro.ruta))
        conexion.commit()
        
        # Verificación después de guardar
        cursor.execute('SELECT id, titulo, categoria, ruta FROM libros WHERE ruta=?', (libro.ruta,))
        row = cursor.fetchone()
        if row:
            print("Libro guardado:")
            print(row)
        else:
            print("Error: No se encontró el libro después de guardarlo.")
    
    except Error as e:
        # Manejo de errores: mostrar el error en un cuadro de diálogo o imprimirlo
        print(f"Error al guardar el libro: {e}")
    
    finally:
        # Cerrar la conexión a la base de datos
        if conexion:
            conexion.close()
            
# Guardar o eliminar un libro de los favoritos en la base de datos
def guardar_favorito(libro):
    # Conectar a la base de datos
    conexion = conectar_db()
    cursor = conexion.cursor()
    # Obtener el ID del libro a partir de su ruta
    resultado = cursor.execute('SELECT id FROM libros WHERE ruta=?', (libro.ruta,)).fetchone()

    if resultado:
        libro_id = resultado[0]

        # Verificar si el libro ya está en favoritos directamente en la base de datos
        favorito_actual = cursor.execute('SELECT 1 FROM favoritos WHERE libro_id=?', (libro_id,)).fetchone()

        try:
            if favorito_actual:
                # Si ya está en favoritos, eliminarlo
                cursor.execute('DELETE FROM favoritos WHERE libro_id=?', (libro_id,))
                print(f"Libro '{libro.ruta}' eliminado de favoritos.")
            else:
                # Si no está en favoritos, agregarlo
                cursor.execute('INSERT INTO favoritos (libro_id) VALUES (?)', (libro_id,))
                print(f"Libro '{libro.ruta}' añadido a favoritos.")

            # Confirmar los cambios en la base de datos
            conexion.commit()

        except sqlite3.Error as e:
            print(f"Error al guardar favorito: {e}")
        
        finally:
            # Cerrar la conexión a la base de datos
            if conexion:
                conexion.close()

    else:
        print(f"El libro con la ruta {libro.ruta} no se encontró en la base de datos.")
    
# Función para obtener categorías desde la base de datos
def get_categorias_from_db():
    try:
        # Conectar a la base de datos
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute('SELECT DISTINCT nombre FROM categorias')
        return [row[0] for row in cursor.fetchall()]
    except Error as e:
        # Manejo de errores: mostrar el error en un cuadro de diálogo o imprimirlo
        print(f"Error al obtener las categorías: {e}")
    
    finally:
        # Cerrar la conexión a la base de datos
        if conexion:
            conexion.close()
            

            
def guardar_cambios_libro(page, libro, nuevo_titulo, nueva_categoria, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        libro.titulo = nuevo_titulo
        libro.categoria = nueva_categoria
        cursor.execute('UPDATE libros SET titulo=?, categoria=? WHERE ruta=?', (libro.titulo, libro.categoria, libro.ruta))
        conexion.commit()
        actualizar_lista_libros(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro)
        cerrar_dialogo(page)
        page.update()
    except Error as e:
        print(f"Error al guardar los cambios del libro: {e}")
    finally:
        if conexion:
            conexion.close()
            

def actualizar_categoria_libro_individual(libros, ruta, nueva_categoria, cursor, conn, page, lista_libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro):
    try:
        libro = next((l for l in libros if l.ruta == ruta), None)
        if libro:
            # Actualizar la categoría en la lista de libros
            libro.categoria = nueva_categoria
            
            # Actualizar la categoría en la base de datos
            cursor.execute('UPDATE libros SET categoria=? WHERE ruta=?', (nueva_categoria, ruta))
            conn.commit()

            # Llamar a actualizar_lista_libros para refrescar la interfaz
            actualizar_lista_libros(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro)

    except Error as e:
        print(f"Error al guardar los cambios del libro: {e}")
    finally:
        if conn:
            conn.close()

def agregar_categoria(
    categoria, ruta, libros, page, lista_libros, favoritos, 
    mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro
):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        if categoria:
            # Si la categoría no existe en la base de datos, la insertamos
            if categoria not in get_categorias_from_db():
                cursor.execute('INSERT INTO categorias (nombre) VALUES (?)', (categoria,))
                conexion.commit()

            # Verifica si la ruta es un directorio o un archivo
            if os.path.isdir(ruta):
                # Aplicar la categoría a todos los libros de la carpeta
                aplicar_categoria_a_libros(
                    page,               # Pasa la página actual, si es necesario
                    categoria,          # La nueva categoría
                    ruta,               # La ruta de la carpeta
                    libros,             # Lista de libros
                    lista_libros,       # Lista visual de los libros
                    favoritos,          # Libros favoritos
                    mostrar_favoritos,  # Función para mostrar favoritos
                    abrir_libro,        # Función para abrir un libro
                    toggle_favorito,    # Función para marcar/desmarcar favoritos
                    eliminar_libro,     # Función para eliminar un libro
                    editar_libro        # Función para editar un libro
                )
            else:
                # Si es un archivo, actualizar solo ese libro
                actualizar_categoria_libro_individual(
                    libros, ruta, categoria, cursor, conexion, 
                    page, lista_libros, favoritos, mostrar_favoritos, 
                    abrir_libro, toggle_favorito, eliminar_libro, editar_libro
                )
        # Cerrar el diálogo después de actualizar
        if cerrar_dialogo:
            cerrar_dialogo(page)

    except Error as e:
        print(f"Error al agregar la categoría: {e}")

    finally:
        if conexion:
            conexion.close()
            
def eliminar_libro(libro, cursor, conn, page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro):
    try:
        # Eliminar el libro de la lista de libros
        if libro in libros:
            libros.remove(libro)

        # Eliminar el libro de la lista de favoritos si está presente
        if libro in favoritos:
            favoritos.remove(libro)

        # Eliminar el libro de la base de datos
        cursor.execute('DELETE FROM libros WHERE ruta=?', (libro.ruta,))
        conn.commit()

        # Actualizar la lista de libros en la interfaz
        actualizar_lista_libros(page, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro, editar_libro)

    except Exception as e:
        # Manejo de errores: mostrar el error en un cuadro de diálogo
        mostrar_mensaje_error(page, f"Error al eliminar el libro: {e}")

def añadir_pdf_desde_url(e, page, pdf_url_field, pdf_name_field, pdf_category_field, lista_libros, libros, favoritos, mostrar_favoritos, abrir_libro, toggle_favorito, eliminar_libro_click_event, editar_libro):
    url = pdf_url_field.value
    name = pdf_name_field.value
    category = pdf_category_field.value

    # Verificar que todos los campos estén completos
    if not url or not name or not category:
        snack_bar = ft.SnackBar(ft.Text("Error: Todos los campos deben estar completos"))
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
        return

    try:
        # Conectar a la base de datos
        conn = conectar_db()
        cursor = conn.cursor()

        # Insertar el nuevo libro en la base de datos
        cursor.execute("""
            INSERT INTO libros (titulo, ruta, categoria) VALUES (?, ?, ?)
        """, (name, url, category))
        conn.commit()

        # Actualizar la lista de libros en memoria (en tu variable `libros`)
        libros.append(Libro(titulo=name, ruta=url, categoria=category))

        # Actualizar la lista de libros en la interfaz
        actualizar_lista_libros(
            page,
            lista_libros,
            libros,
            favoritos,
            mostrar_favoritos,
            abrir_libro,
            toggle_favorito,
            eliminar_libro_click_event,
            editar_libro
        )

        # Mostrar un SnackBar con mensaje de éxito
        snack_bar = ft.SnackBar(ft.Text("Libro añadido con éxito"))
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

        # Cerrar el diálogo después de añadir el libro
        cerrar_dialogo(page)

    except Exception as ex:
        snack_bar = ft.SnackBar(ft.Text(f"Error al guardar el libro: {str(ex)}"))
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    finally:
        if conn:
            conn.close()
