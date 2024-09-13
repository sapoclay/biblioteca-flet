import flet as ft

def toggle_tema(page: ft.Page, tema_oscuro: bool) -> bool:
    tema_oscuro = not tema_oscuro
    page.theme_mode = ft.ThemeMode.DARK if tema_oscuro else ft.ThemeMode.LIGHT
    page.update()
    return tema_oscuro