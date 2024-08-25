import PySimpleGUI as sg
import sqlite3
from datetime import datetime

# Configuração inicial do banco de dados SQLite
def setup_db():
    conn = sqlite3.connect('registros.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etiqueta_copo TEXT,
            etiqueta_placa TEXT,
            input_time TEXT,
            testador_id INTEGER,
            debug_id INTEGER,
            debug_time TEXT,
            reparadora_id INTEGER,
            repair_time TEXT,
            observacao TEXT,
            componentes TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS testadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debuggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reparadoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
    ''')
    conn.commit()
    conn.close()

setup_db()

# Função para obter listas de IDs e nomes
def get_list_from_db(table):
    conn = sqlite3.connect('registros.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, nome FROM {table}")
    records = cursor.fetchall()
    conn.close()
    return [f'{record[0]} - {record[1]}' for record in records]

# Função para obter registros do banco de dados
def get_registros():
    conn = sqlite3.connect('registros.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, etiqueta_copo FROM registros")
    registros = cursor.fetchall()
    conn.close()
    return registros

# Layout da interface Menu
layout_menu = [
    [sg.Text("Busca pela Etiqueta"), sg.Input(key="buscar_etiqueta"), sg.Button("Buscar")],
    [sg.Button("Novo Registro")],
    [sg.Text("Registros:")],
    [sg.Listbox(values=[f'{registro[0]} - {registro[1]}' for registro in get_registros()], size=(100, 20), key="registros", enable_events=True)]
]

# Função para criar a janela de criação de registro
def janela_create():
    layout_create = [
        [sg.Text("Etiqueta Copo"), sg.Input(key="etiqueta_copo")],
        [sg.Text("Etiqueta Placa"), sg.Input(key="etiqueta_placa")],
        [sg.Input(key="Input Time", visible=False)], #adicionar o tempo somente quando apertar o botão criar
        [sg.Text("Testador"), sg.Combo(get_list_from_db('testadores'), key="testador"), sg.Button("Adicionar Testador")],
        [sg.Text("Debug"), sg.Combo(get_list_from_db('debuggers'), key="debug"), sg.Button("Adicionar Debug")],
        [sg.Input(key="Debug Time", visible=False)], #adicionar o tempo somente quando selecionado um debug
        [sg.Text("Reparadora"), sg.Combo(get_list_from_db('reparadoras'), key="reparadora"), sg.Button("Adicionar Reparadora")],
        [sg.Input(key="Repair Time", visible=False)], #adicionar o tempo somente quando selecionado uma reparadora
        [sg.Text("Componente"), sg.Input(key="componente_temp"), sg.Button("Adicionar Componente")],
        [sg.Listbox(values=[], size=(40, 5), key="lista_componentes", enable_events=True)],
        [sg.Text("Observação"), sg.Input(key="observacao")],
        [sg.Button("Criar")]
    ]
    return sg.Window("Novo Registro", layout_create, finalize=True)

# Função para criar a janela de atualização de registro
def janela_update(dados):
    layout_update = [
        [sg.Text("Etiqueta Copo"), sg.Input(key="etiqueta_copo")],
        [sg.Text("Etiqueta Placa"), sg.Input(key="etiqueta_placa")],
        [sg.Text("Input Time"), sg.Input(key="input_time", disabled=True)],
        [sg.Text("Testador"), sg.Combo(get_list_from_db('testadores'), key="testador"), sg.Button("Adicionar Testador")],
        [sg.Text("Debug"), sg.Combo(get_list_from_db('debuggers'), key="debug"), sg.Button("Adicionar Debug")],
        [sg.Text("Debug Time"), sg.Input(key="debug_time", disabled=True)], #adicionar o tempo somente quando selecionado um debug
        [sg.Text("Reparadora"), sg.Combo(get_list_from_db('reparadoras'), key="reparadora"), sg.Button("Adicionar Reparadora")],
        [sg.Text("Repair Time"), sg.Input(key="repair_time", disabled=True)], #adicionar o tempo somente quando selecionado uma reparadora
        [sg.Text("Componente"), sg.Input(key="componente_temp"), sg.Button("Adicionar Componente")],
        [sg.Listbox(values=[], size=(40, 5), key="lista_componentes", enable_events=True)],
        [sg.Text("Observação"), sg.Input(key="observacao")],
        [sg.Button("Atualizar"), sg.Button("Excluir"), sg.Button("Cancelar")]
    ]
    
    janela = sg.Window("Atualizar Registro", layout_update, finalize=True)
    for key in dados:
        if key == 'lista_componentes':
            janela[key].update(values=dados[key])
        else:
            janela[key].update(value=dados[key])
    return janela

# Função para adicionar componente à lista
def adicionar_componente(componente, lista_componentes):
    if componente and componente not in lista_componentes:
        lista_componentes.append(componente)
    return lista_componentes

# Função para remover componente da lista
def remover_componente(componente, lista_componentes):
    if componente in lista_componentes:
        lista_componentes.remove(componente)
    return lista_componentes

# Função principal de execução
janela = sg.Window("Menu Principal", layout_menu)

while True:
    evento, valores = janela.read()
    if evento == sg.WINDOW_CLOSED:
        break
    
    if evento == "Novo Registro":
        janela.hide()
        janela_novo_registro = janela_create()
        componentes_temporarios = []

        while True:
            evento_novo, valores_novo = janela_novo_registro.read()
            if evento_novo == sg.WINDOW_CLOSED or evento_novo == "Cancelar":
                janela_novo_registro.close()
                janela.un_hide()
                break
            
            if evento_novo == "Adicionar Testador":
                nome_testador = sg.popup_get_text("Nome do Testador:")
                if nome_testador:
                    conn = sqlite3.connect('registros.db')
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO testadores (nome) VALUES (?)', (nome_testador,))
                    conn.commit()
                    conn.close()
                    janela_novo_registro['testador'].update(values=get_list_from_db('testadores'))
            
            if evento_novo == "Adicionar Debug":
                nome_debugger = sg.popup_get_text("Nome do Debugger:")
                if nome_debugger:
                    conn = sqlite3.connect('registros.db')
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO debuggers (nome) VALUES (?)', (nome_debugger,))
                    conn.commit()
                    conn.close()
                    janela_novo_registro['debug'].update(values=get_list_from_db('debuggers'))
            
            if evento_novo == "Adicionar Reparadora":
                nome_reparadora = sg.popup_get_text("Nome da Reparadora:")
                if nome_reparadora:
                    conn = sqlite3.connect('registros.db')
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO reparadoras (nome) VALUES (?)', (nome_reparadora,))
                    conn.commit()
                    conn.close()
                    janela_novo_registro['reparadora'].update(values=get_list_from_db('reparadoras'))
            
            if evento_novo == "Adicionar Componente":
                componente_temp = valores_novo['componente_temp']
                if componente_temp:
                    componentes_temporarios = adicionar_componente(componente_temp, componentes_temporarios)
                    janela_novo_registro['lista_componentes'].update(values=componentes_temporarios)
                    janela_novo_registro['componente_temp'].update('')
            
            if evento_novo == "Criar":
                debug_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if valores_novo['debug'] else ''
                repair_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if valores_novo['reparadora'] else ''
                
                conn = sqlite3.connect('registros.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO registros (
                        etiqueta_copo, 
                        etiqueta_placa, 
                        input_time, 
                        testador_id, 
                        debug_id, 
                        debug_time, 
                        reparadora_id, 
                        repair_time, 
                        observacao, 
                        componentes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    valores_novo['etiqueta_copo'],
                    valores_novo['etiqueta_placa'],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    int(valores_novo['testador'].split(' ')[0]) if valores_novo['testador'] else None,
                    int(valores_novo['debug'].split(' ')[0]) if valores_novo['debug'] else None,
                    debug_time,
                    int(valores_novo['reparadora'].split(' ')[0]) if valores_novo['reparadora'] else None,
                    repair_time,
                    valores_novo['observacao'],
                    ','.join(componentes_temporarios)
                ))
                conn.commit()
                conn.close()
                janela_novo_registro['etiqueta_copo'].update('')
                janela_novo_registro['etiqueta_placa'].update('')
                janela_novo_registro['testador'].update('')
                janela_novo_registro['debug'].update('')
                janela_novo_registro['reparadora'].update('')
                janela_novo_registro['componente_temp'].update('')
                janela_novo_registro['observacao'].update('')
                janela_novo_registro['lista_componentes'].update(values=[])
                sg.popup('Registro criado com sucesso!')
                
                # Atualizar a listbox de registros no Menu
                janela['registros'].update(values=[f'{registro[0]} - {registro[1]}' for registro in get_registros()])
        
    if evento == "Buscar":
        etiqueta = valores['buscar_etiqueta']
        conn = sqlite3.connect('registros.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM registros WHERE etiqueta_copo=? OR etiqueta_placa=?', (etiqueta, etiqueta))
        dados = cursor.fetchone()
        conn.close()
        if dados:
            dados_dict = {
                'etiqueta_copo': dados[1],
                'etiqueta_placa': dados[2],
                'input_time': dados[3],
                'testador': f"{dados[4]} - {get_list_from_db('testadores')[dados[4]-1].split(' - ')[1]}" if dados[4] else '',
                'debug': f"{dados[5]} - {get_list_from_db('debuggers')[dados[5]-1].split(' - ')[1]}" if dados[5] else '',
                'debug_time': dados[6],
                'reparadora': f"{dados[7]} - {get_list_from_db('reparadoras')[dados[7]-1].split(' - ')[1]}" if dados[7] else '',
                'repair_time': dados[8],
                'observacao': dados[9]
            }
            componentes = dados[10].split(',') if dados[10] else []
            dados_dict['lista_componentes'] = componentes
            janela.hide()
            janela_atualizar_registro = janela_update(dados_dict)

            while True:
                evento_update, valores_update = janela_atualizar_registro.read()
                if evento_update == sg.WINDOW_CLOSED or evento_update == "Cancelar":
                    janela_atualizar_registro.close()
                    janela.un_hide()
                    break
                
                if evento_update == "Adicionar Testador":
                    nome_testador = sg.popup_get_text("Nome do Testador:")
                    if nome_testador:
                        conn = sqlite3.connect('registros.db')
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO testadores (nome) VALUES (?)', (nome_testador,))
                        conn.commit()
                        conn.close()
                        janela_atualizar_registro['testador'].update(values=get_list_from_db('testadores'))
                
                if evento_update == "Adicionar Debug":
                    nome_debugger = sg.popup_get_text("Nome do Debugger:")
                    if nome_debugger:
                        conn = sqlite3.connect('registros.db')
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO debuggers (nome) VALUES (?)', (nome_debugger,))
                        conn.commit()
                        conn.close()
                        janela_atualizar_registro['debug'].update(values=get_list_from_db('debuggers'))
                
                if evento_update == "Adicionar Reparadora":
                    nome_reparadora = sg.popup_get_text("Nome da Reparadora:")
                    if nome_reparadora:
                        conn = sqlite3.connect('registros.db')
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO reparadoras (nome) VALUES (?)', (nome_reparadora,))
                        conn.commit()
                        conn.close()
                        janela_atualizar_registro['reparadora'].update(values=get_list_from_db('reparadoras'))
                
                if evento_update == "Adicionar Componente":
                    componente_temp = valores_update['componente_temp']
                    if componente_temp:
                        componentes_temporarios = adicionar_componente(componente_temp, componentes_temporarios)
                        janela_atualizar_registro['lista_componentes'].update(values=componentes_temporarios)
                        janela_atualizar_registro['componente_temp'].update('')
                
                if evento_update == "Atualizar":
                    debug_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if valores_update['debug'] else ''
                    repair_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if valores_update['reparadora'] else ''
                    
                    conn = sqlite3.connect('registros.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE registros SET
                        etiqueta_copo = ?, 
                        etiqueta_placa = ?, 
                        testador_id = ?, 
                        debug_id = ?, 
                        debug_time = ?, 
                        reparadora_id = ?, 
                        repair_time = ?, 
                        observacao = ?,
                        componentes = ?
                        WHERE id = ?
                    ''', (
                        valores_update['etiqueta_copo'],
                        valores_update['etiqueta_placa'],
                        int(valores_update['testador'].split(' ')[0]) if valores_update['testador'] else None,
                        int(valores_update['debug'].split(' ')[0]) if valores_update['debug'] else None,
                        debug_time,
                        int(valores_update['reparadora'].split(' ')[0]) if valores_update['reparadora'] else None,
                        repair_time,
                        valores_update['observacao'],
                        ','.join(componentes_temporarios),
                        dados[0]
                    ))
                    conn.commit()
                    conn.close()
                    sg.popup('Registro atualizado com sucesso!')
                    janela_atualizar_registro.close()
                    janela.un_hide()
                    
                    # Atualizar a listbox de registros no Menu
                    janela['registros'].update(values=[f'{registro[0]} - {registro[1]}' for registro in get_registros()])
                    break
                
                if evento_update == "Excluir":
                    confirmar_exclusao = sg.popup_yes_no('Deseja realmente excluir este registro?', title='Confirmação de Exclusão')
                    if confirmar_exclusao == 'Yes':
                        conn = sqlite3.connect('registros.db')
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM registros WHERE id=?', (dados[0],))
                        conn.commit()
                        conn.close()
                        sg.popup('Registro excluído com sucesso!')
                        janela_atualizar_registro.close()
                        janela.un_hide()
                        break

janela.close()
