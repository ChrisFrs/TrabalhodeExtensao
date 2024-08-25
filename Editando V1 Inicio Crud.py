import PySimpleGUI as sg
import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('repairs.db')
c = conn.cursor()

# Criar tabela de reparos se não existir
c.execute('''
CREATE TABLE IF NOT EXISTS repairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etiqueta TEXT NOT NULL,
    testador TEXT NOT NULL,
    componentes TEXT
)
''')

# Criar tabela de testadores se não existir
c.execute('''
CREATE TABLE IF NOT EXISTS testers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

conn.commit()
conn.close()

# Funções para operações CRUD de testadores
def create_tester(name):
    conn = sqlite3.connect('repairs.db')
    c = conn.cursor()
    c.execute("INSERT INTO testers (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def read_testers():
    conn = sqlite3.connect('repairs.db')
    c = conn.cursor()
    c.execute("SELECT name FROM testers")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Funções para operações CRUD de reparos
def create_repair(etiqueta, testador, componentes):
    conn = sqlite3.connect('repairs.db')
    c = conn.cursor()
    c.execute("INSERT INTO repairs (etiqueta, testador, componentes) VALUES (?, ?, ?)", (etiqueta, testador, componentes))
    conn.commit()
    conn.close()

def read_repairs():
    conn = sqlite3.connect('repairs.db')
    c = conn.cursor()
    c.execute("SELECT etiqueta FROM repairs")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def read_repair_by_etiqueta(etiqueta):
    conn = sqlite3.connect('repairs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM repairs WHERE etiqueta = ?", (etiqueta,))
    row = c.fetchone()
    conn.close()
    return row

def update_repair(id, etiqueta, testador, componentes):
    conn = sqlite3.connect('repairs.db')
    c = conn.cursor()
    c.execute("UPDATE repairs SET etiqueta = ?, testador = ?, componentes = ? WHERE id = ?", (etiqueta, testador, componentes, id))
    conn.commit()
    conn.close()

def delete_repair(id):
    conn = sqlite3.connect('repairs.db')
    c = conn.cursor()
    c.execute("DELETE FROM repairs WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# Funções para operações CRUD de testadores
def create_tester(name):
    conn = sqlite3.connect('repairs.db')
    c = conn.cursor()
    c.execute("INSERT INTO testers (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def read_testers():
    conn = sqlite3.connect('repairs.db')
    c = conn.cursor()
    c.execute("SELECT name FROM testers")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Lista para armazenar componentes temporários
componentes = []

# Carregar testadores do banco de dados
tester_ids = read_testers()

# Layout da interface gráfica
layout = [
    [sg.Text("Busca pela Etiqueta"), sg.Input(key="buscar_etiqueta"), sg.Button("Buscar")],
    [sg.Text("Etiqueta"), sg.Input(key="etiqueta")],
    [sg.Text("Testador"), sg.Combo(tester_ids, key="testador", enable_events=True), sg.Button("Adicionar Testador")],
    [sg.Text("Componente"), sg.Input(key="componente"), sg.Button("Adicionar Componente")],
    [sg.Text("Componentes"), sg.Listbox(values=componentes, size=(40, 5), key="lista_componentes", enable_events=True)],
    [sg.Button("Criar")],
    [sg.Text("Registros:"), sg.Multiline(size=(100, 10), key="registros", disabled=True)]
]

# Criar a janela
window = sg.Window("CRUD de Reparos", layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == "Criar":
        etiqueta = values["etiqueta"]
        testador = values["testador"]
        componentes_str = ', '.join(componentes)
        create_repair(etiqueta, testador, componentes_str)
        sg.popup("Reparo criado com sucesso!")
        componentes = []
        window["etiqueta"].update('')
        window["testador"].update('')
        window["componente"].update('')
        window["lista_componentes"].update(componentes)
        window["registros"].update('\n'.join(read_repairs()))
    elif event == "Buscar":
        etiqueta = values["buscar_etiqueta"]
        repair = read_repair_by_etiqueta(etiqueta)
        if repair:
            sg.popup(f"Etiqueta: {repair[1]}\nTestador: {repair[2]}\nComponentes: {repair[3]}")
            # Abre uma nova janela para atualizar os dados
            update_layout = [
                [sg.Text("Etiqueta"), sg.Input(repair[1], key="etiqueta")],
                [sg.Text("Testador"), sg.Combo(tester_ids, default_value=repair[2], key="testador")],
                [sg.Text("Componente"), sg.Input(key="componente"), sg.Button("Adicionar Componente")],
                [sg.Text("Componentes"), sg.Listbox(values=repair[3].split(', '), size=(40, 5), key="lista_componentes", enable_events=True)],
                [sg.Button("Atualizar"), sg.Button("Deletar")]
            ]
            update_window = sg.Window("Atualizar Reparo", update_layout)
            componentes_update = repair[3].split(', ')
            while True:
                update_event, update_values = update_window.read()
                if update_event == sg.WIN_CLOSED:
                    break
                elif update_event == "Adicionar Componente":
                    componente = update_values["componente"]
                    if componente:
                        componentes_update.append(componente)
                        update_window["lista_componentes"].update(componentes_update)
                        update_window["componente"].update('')
                elif update_event == "lista_componentes":
                    selected_componente = update_values["lista_componentes"]
                    if selected_componente:
                        componentes_update.remove(selected_componente[0])
                        update_window["lista_componentes"].update(componentes_update)
                elif update_event == "Atualizar":
                    etiqueta = update_values["etiqueta"]
                    testador = update_values["testador"]
                    componentes_str = ', '.join(componentes_update)
                    update_repair(repair[0], etiqueta, testador, componentes_str)
                    sg.popup("Reparo atualizado com sucesso!")
                    update_window.close()
                elif update_event == "Deletar":
                    delete_repair(repair[0])
                    sg.popup("Reparo deletado com sucesso!")
                    update_window.close()
            window["registros"].update('\n'.join(read_repairs()))
        else:
            sg.popup("Etiqueta não encontrada!")
    elif event == "Adicionar Componente":
        componente = values["componente"]
        if componente:
            componentes.append(componente)
            window["lista_componentes"].update(componentes)
            window["componente"].update('')
    elif event == "Adicionar Testador":
        new_tester = sg.popup_get_text("Nome do novo testador:")
        if new_tester:
            create_tester(new_tester)
            tester_ids = read_testers()
            window["testador"].update(values=tester_ids)
            sg.popup(f"Testador '{new_tester}' adicionado com sucesso!")
    elif event == "lista_componentes":
        selected_componente = values["lista_componentes"]
        if selected_componente:
            componentes.remove(selected_componente[0])
            window["lista_componentes"].update(componentes)

window.close()
