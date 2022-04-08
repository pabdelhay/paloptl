class Distrito:
    nome = ""
    dialecto = ""
    postos_admin = []
    sucos = []
    aldeias = []

    def print_nome_and_dialecto(self):
        print(f"{self.name} - {self.dialecto}")

# CRIANDO DISTRITO
d = Distrito()
d.name = "Dili"
d.dialecto = "Tetum"
d.postos_admin = ["Cristo Rei", "Dom Aleixo"]
d.sucos = ["Comoro", "Bidau Santana"]
d.aldeias = ["Terus Nanis", "Manu Mata"]

d.print_nome_and_dialecto()