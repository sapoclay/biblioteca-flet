class Libro:
    def __init__(self, titulo, categoria, ruta):
        self.titulo = titulo
        self.categoria = categoria
        self.ruta = ruta

    def to_dict(self):
        return {"titulo": self.titulo, "categoria": self.categoria, "ruta": self.ruta}