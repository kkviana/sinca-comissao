import csv
from cliente.models import Cliente

def load_data_from_csv(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula a primeira linha do arquivo CSV (que pode ser um cabeçalho)
        for row in reader:
            cliente = Cliente(nome=row[0])
            cliente.save()
