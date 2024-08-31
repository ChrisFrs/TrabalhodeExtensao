import PySimpleGUI as sg
import sqlite3
from datetime import datetime
import pandas as pd
import os

# Definindo o caminho do banco de dados em um subdiretório de C:\
db_dir = r'C:\Meu_banco_Python'
db_path = os.path.join(db_dir, 'registros.db')

# Certifica-se de que o diretório exista
os.makedirs(db_dir, exist_ok=True)

# Configuração inicial do banco de dados SQLite
def setup_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qrcode_copo TEXT,
            qrcode_placa TEXT,
            input_time TEXT,
            testador_id INTEGER,
            debug_id INTEGER,
            debug_time TEXT,
            reparadora_id INTEGER,
            repair_time TEXT,
            componentes TEXT,
            observacao TEXT
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registro_id INTEGER,
            qrcode_copo TEXT,
            qrcode_placa TEXT,
            input_time TEXT,
            testador_nome INTEGER,
            debug_nome INTEGER,
            debug_time TEXT,
            reparadora_nome INTEGER,
            repair_time TEXT,
            componentes TEXT,
            observacao TEXT,
            data_alteracao TEXT,
            FOREIGN KEY (registro_id) REFERENCES registros(id)
        )
    ''')         
    conn.commit()
    conn.close()

setup_db()

# Função para obter listas de IDs e nomes
def get_list_from_db(table):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, nome FROM {table}")
    records = cursor.fetchall()
    conn.close()
    return [f'{record[0]} - {record[1]}' for record in records]

# Função para obter registros do banco de dados
def get_registros():
    # Conectar ao banco de dados
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT qrcode_copo, qrcode_placa, input_time FROM registros
            ORDER BY input_time DESC
        ''')
        registros = cursor.fetchall()
    return registros

# Layout da interface Menu
layout_menu = [
    [sg.Text("Busca pela Etiqueta"), sg.Input(size=(26), key="buscar_etiqueta"), sg.Button("Buscar"), sg.Button('Importar Excel'), sg.Button('Exportar por Data')],
    [sg.Button("Novo Registro")], 
    [sg.Text("Registros: QRCode Copo                      QRCode Placa")],
    [sg.Listbox(values=[f'{registro[0]} - {registro[1]}' for registro in get_registros()], size=(100, 10), key="registros", enable_events=True)]
]

# Função para mostrar a janela de seleção de datas e exportar dados
def show_export_date_window():
    layout = [
        [sg.Text('Data Inicial (DD-MM-YYYY):'), sg.Input(size=(10), key='data_inicial')],
        [sg.Text('Data Final (DD-MM-YYYY):'), sg.Input(size=(10), key='data_final')],
        [sg.Button('Exportar'), sg.Button('Exportar Todos'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Exportar por Data', layout)

    while True:
        evento, valores = window.read()

        if evento == sg.WINDOW_CLOSED or evento == 'Cancelar':
            break
         
        if evento == 'Exportar':
            start_date = valores['data_inicial']
            end_date = valores['data_final']
            if start_date and end_date:
                try:
                    # Converte as strings de data para o formato datetime para validar
                    datetime.strptime(start_date, "%d-%m-%Y")
                    datetime.strptime(end_date, "%d-%m-%Y")
                    export_to_csv(start_date, end_date)
                    window.close()
                except ValueError:
                    sg.popup('Por favor, insira datas válidas no formato DD-MM-YYYY.')
            else:
                sg.popup('Por favor, preencha ambas as datas.')

        elif evento == 'Exportar Todos':
            # Define o intervalo de datas para cobrir todos os registros
            export_to_csv('01-01-1990', '31-12-2100')  # Aqui estamos usando datas amplas para cobrir todos os registros

    window.close()
    

# Função para criar a janela de criação de registro
def janela_create():
    layout_create = [
        [sg.Text("Etiqueta Copo"), sg.Input(size=(26), key="qrcode_copo")],
        [sg.Text("Etiqueta Placa"), sg.Input(size=(26), key="qrcode_placa")],
        [sg.Input(key="Input Time", visible=False)], #adicionar o tempo somente quando apertar o botão criar
        [sg.Text("Testador"), sg.Combo(get_list_from_db('testadores'), key="testador"), sg.Button("Adicionar Testador")],
        [sg.Text("Debug"), sg.Combo(get_list_from_db('debuggers'), key="debug"), sg.Button("Adicionar Debug")],
        [sg.Input(key="Debug Time", visible=False)], #adicionar o tempo somente quando selecionado um debug
        [sg.Text("Reparadora"), sg.Combo(get_list_from_db('reparadoras'), key="reparadora"), sg.Button("Adicionar Reparadora")],
        [sg.Input(key="Repair Time", visible=False)], #adicionar o tempo somente quando selecionado uma reparadora
        [sg.Text("Componente"), sg.Input(size=(10),key="componente_temp"), sg.Button("Adicionar Componente"), sg.Button("Remover Componente")],
        [sg.Listbox(values=[], size=(30, 5), key="lista_componentes", enable_events=True)],
        [sg.Text("Observação"), sg.Input(key="observacao")],
        [sg.Button("Criar")]
    ]
    return sg.Window("Novo Registro", layout_create, finalize=True)

# Função para criar a janela de atualização de registro
def janela_update(dados):
    layout_update = [
        [sg.Text("Etiqueta Copo"), sg.Input(size=(26), key="qrcode_copo")],
        [sg.Text("Etiqueta Placa"), sg.Input(size=(26), key="qrcode_placa")],
        [sg.Text("Input Time"), sg.Input(key="input_time", disabled=True)],
        [sg.Text("Testador"), sg.Combo(get_list_from_db('testadores'), key="testador"), sg.Button("Adicionar Testador")],
        [sg.Text("Debug"), sg.Combo(get_list_from_db('debuggers'), key="debug"), sg.Button("Adicionar Debug")],
        [sg.Text("Debug Time"), sg.Input(key="debug_time", disabled=True)], #adicionar o tempo somente quando selecionado um debug
        [sg.Text("Reparadora"), sg.Combo(get_list_from_db('reparadoras'), key="reparadora"), sg.Button("Adicionar Reparadora")],
        [sg.Text("Repair Time"), sg.Input(key="repair_time", disabled=True)], #adicionar o tempo somente quando selecionado uma reparadora
        [sg.Text("Componente"), sg.Input(size=(10),key="componente_temp"), sg.Button("Adicionar Componente"), sg.Button("Remover Componente")],
        [sg.Listbox(values=[], size=(40, 5), key="lista_componentes", enable_events=True)],
        [sg.Text("Observação"), sg.Input(key="observacao")],
        [sg.Button("Atualizar"),sg.Button("Ver Histórico"), sg.Button("Excluir"), sg.Button("Cancelar"), sg.Button('Exportar Modificacoes')]
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


# Função para exportar dados para CSV filtrando por data
def export_to_csv(start_date, end_date):
    import csv
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Consulta SQL com JOIN para pegar os nomes em vez do id
    cursor.execute('''
        SELECT registros.id, qrcode_copo, qrcode_placa, input_time, 
               testadores.nome AS testador_nome, 
               debuggers.nome AS debugger_nome, debug_time, 
               reparadoras.nome AS reparadora_nome, repair_time, 
               componentes, observacao
        FROM registros
        LEFT JOIN testadores ON registros.testador_id = testadores.id
        LEFT JOIN debuggers ON registros.debug_id = debuggers.id
        LEFT JOIN reparadoras ON registros.reparadora_id = reparadoras.id
        WHERE input_time BETWEEN ? AND ?
                ORDER BY input_time
    ''', (start_date, end_date))
    
    records = cursor.fetchall()
    conn.close()

    with open('registros_exportados.csv', mode='w', newline='', encoding='utf-16') as file:
        writer = csv.writer(file)
        # Escrevendo os nomes das colunas
        writer.writerow(['ID', 'QR Code Copo', 'QR Code Placa', 'Hora de Entrada', 'Nome do Testador', 'Nome do Debugger', 'Hora do Debug', 'Nome da Reparadora', 'Hora do Reparo', 'Componentes', 'Observacao'])
        # Escrevendo os dados
        writer.writerows(records)

    sg.popup('Dados exportados com sucesso para registros_exportados.csv!')
    
# Função para exportar atualizações peça para CSV
def export_to_csvat():
    import csv
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT historico.id, qrcode_copo, qrcode_placa, input_time, 
               testador_nome, debug_nome, debug_time, reparadora_nome, repair_time, 
               componentes, observacao, data_alteracao
        FROM historico ORDER BY qrcode_placa
    ''')
    
    records = cursor.fetchall()
    conn.close()

    with open('registros_modificoes.csv', mode='w', newline='', encoding='utf-16') as file:
        writer = csv.writer(file)
        # Escrevendo os nomes das colunas
        writer.writerow(['ID', 'QR Code Copo', 'QR Code Placa', 'Hora de Entrada', 'Nome do Testador', 'Nome do Debug', 'Hora do Debug', 'Nome da Reparadora', 'Hora do Reparo', 'Componentes', 'Observacao', 'Data Alteracao',])
        # Escrevendo os dados
        writer.writerows(records)

    sg.popup('Dados exportados com sucesso para registros_modificoes.csv!')

def mostrar_historico(id_registro):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT qrcode_copo, qrcode_placa, input_time, testador_nome, debug_nome, debug_time, reparadora_nome, repair_time, componentes, observacao, data_alteracao FROM historico WHERE registro_id = ?', (id_registro,))
                historico_dados = cursor.fetchall()
                conn.close()

                if not historico_dados:
                    sg.popup('Nenhum histórico encontrado para este registro.')
                    return

                # Variáveis de controle de paginação
                pagina_atual = 0
                itens_por_pagina = 10
                total_paginas = (len(historico_dados) + itens_por_pagina - 1) // itens_por_pagina

                layout_historico = [
                    [sg.Table(values=historico_dados[0:itens_por_pagina], headings=['QRCode Copo','QRCode Placa','Entrada Time','Testador', 'Debug', 'Debug Time', 'Reparadora', 'Reparadora Time', 'Componentes', 'Observacao', 'Data de Alteração'], 
                            key='-TABELA_HISTORICO-', display_row_numbers=False, auto_size_columns=True)],
                    [sg.Button('<< Anterior'), sg.Text(f'Página {pagina_atual + 1} de {total_paginas}', key='-PAGINA-'), sg.Button('Próximo >>')],
                    [sg.Button('Fechar')]
                ]

                janela_historico = sg.Window('Histórico de Alterações', layout_historico)

                while True:
                    evento_hist, valores_hist = janela_historico.read()
                    if evento_hist == sg.WINDOW_CLOSED or evento_hist == 'Fechar':
                        janela_historico.close()
                        break
                    elif evento_hist == '<< Anterior' and pagina_atual > 0:
                        pagina_atual -= 1
                    elif evento_hist == 'Próximo >>' and pagina_atual < total_paginas - 1:
                        pagina_atual += 1
                        
                    
                    # Atualiza a tabela de acordo com a página atual
                    inicio = pagina_atual * itens_por_pagina
                    fim = inicio + itens_por_pagina
                    janela_historico['-TABELA_HISTORICO-'].update(values=historico_dados[inicio:fim])
                    janela_historico['-PAGINA-'].update(f'Página {pagina_atual + 1} de {total_paginas}')

# Função principal de execução
janela = sg.Window("Menu Principal", layout_menu)

while True:
    evento, valores = janela.read()
    if evento == sg.WINDOW_CLOSED:
        break

    if evento == 'Exportar Todos':
        export_to_csv('01-01-1900', '31-12-2100')  # Exporta todos os registros por padrão
    elif evento == 'Exportar por Data':
        show_export_date_window()

    if evento == 'Importar Excel':
        file_path = sg.popup_get_file('Escolha um arquivo Excel', file_types=(("Excel Files", "*.xlsx"),))
        if file_path:
            try:
                # Ler o arquivo Excel
                df = pd.read_excel(file_path)
                
                # Conectar ao banco de dados
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()

                    # Conjunto para rastrear registros únicos e válidos
                    registros_validos = set()

                    # Contadores para duplicados
                    copo_duplicados = 0
                    placa_duplicados = 0

                    # Definir o input_time uma vez
                    input_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                    # Inserir cada linha do Excel no banco de dados
                    for index, row in df.iterrows():
                        qrcode_copo = row['QRCode Copo']
                        qrcode_placa = row['QRCode Placa']

                        # Verificar se os campos estão vazios
                        if pd.isna(qrcode_copo) or pd.isna(qrcode_placa):
                            continue  # Pular registros com campos vazios

                        # Normalizar os dados para checar duplicidade
                        registro = (qrcode_copo, qrcode_placa)

                        # Verificar duplicidade dentro do próprio arquivo Excel
                        if registro in registros_validos:
                            # Incrementar contadores de duplicados internos
                            copo_duplicados += 1
                            placa_duplicados += 1
                            continue  # Pular duplicados internos

                        # Checar se o registro já existe no banco de dados
                        cursor.execute('''
                            SELECT COUNT(*) FROM registros 
                            WHERE qrcode_copo = ? OR qrcode_placa = ?
                        ''', (qrcode_copo, qrcode_placa))
                        
                        resultado = cursor.fetchone()[0]

                        if resultado > 0:
                            # Incrementar contadores de duplicados no banco de dados
                            if cursor.execute('SELECT COUNT(*) FROM registros WHERE qrcode_copo = ?', (qrcode_copo,)).fetchone()[0] > 0:
                                copo_duplicados += 1
                            if cursor.execute('SELECT COUNT(*) FROM registros WHERE qrcode_placa = ?', (qrcode_placa,)).fetchone()[0] > 0:
                                placa_duplicados += 1
                            continue  # Pular registros duplicados no banco de dados

                        # Adicionar registros válidos ao conjunto
                        registros_validos.add(registro)

                    # Inserir todos os registros válidos no banco de dados
                    if registros_validos:
                        cursor.executemany('''
                            INSERT INTO registros (qrcode_copo, qrcode_placa, input_time, testador_id, debug_id, debug_time, reparadora_id, repair_time, componentes, observacao)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', [(qrcode_copo, qrcode_placa, input_time, None, None, None, None, None, None, None) for qrcode_copo, qrcode_placa in registros_validos])

                    conn.commit()
                    
                    # Exibir mensagem final com quantidade de duplicados ignorados
                    sg.popup(f"Importação concluída com sucesso!\n"
                            f"Duplicados ignorados: {copo_duplicados} QRCode Copo e {placa_duplicados} QRCode Placa.")
                    
                    # Atualizar a listbox de registros no Menu
                    registros = get_registros()  # Obtém os registros ordenados
                    janela['registros'].update(values=[f'{registro[0]} - {registro[1]}' for registro in registros])

            except Exception as e:
                sg.popup_error(f"Ocorreu um erro ao importar o arquivo: {e}")

                    
    if evento == "Novo Registro":
        janela.hide()
        janela_novo_registro = janela_create()
        componentes_temporarios = []
                
        # Conexão aberta durante a execução da janela de novo registro
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        while True:
            evento_novo, valores_novo = janela_novo_registro.read()
            if evento_novo == sg.WINDOW_CLOSED or evento_novo == "Cancelar":
                janela_novo_registro.close()
                janela.un_hide()
                conn.close()  # Fechando a conexão aqui após terminar a janela
                break
            
            if evento_novo == "Adicionar Testador":
                nome_testador = sg.popup_get_text("Nome do Testador:")
                if nome_testador:
                    cursor.execute('INSERT INTO testadores (nome) VALUES (?)', (nome_testador.strip(),))
                    conn.commit()
                    janela_novo_registro['testador'].update(values=get_list_from_db('testadores'))
            
            if evento_novo == "Adicionar Debug":
                nome_debugger = sg.popup_get_text("Nome do Debugger:")
                if nome_debugger:
                    cursor.execute('INSERT INTO debuggers (nome) VALUES (?)', (nome_debugger.strip(),))
                    conn.commit()
                    janela_novo_registro['debug'].update(values=get_list_from_db('debuggers'))
            
            if evento_novo == "Adicionar Reparadora":
                nome_reparadora = sg.popup_get_text("Nome da Reparadora:")
                if nome_reparadora:
                    cursor.execute('INSERT INTO reparadoras (nome) VALUES (?)', (nome_reparadora.strip(),))
                    conn.commit()
                    janela_novo_registro['reparadora'].update(values=get_list_from_db('reparadoras'))
            
            if evento_novo == "Adicionar Componente":
                componente_temp = valores_novo['componente_temp']
                
                # Verificação para evitar a inserção de valores vazios ou somente espaços
                if not componente_temp:
                    sg.popup("O campo de componente está vazio. Por favor, insira um valor válido.")
                else:
                    if componente_temp:
                        componentes_temporarios = adicionar_componente(componente_temp, componentes_temporarios)
                        janela_novo_registro['lista_componentes'].update(values=componentes_temporarios)
                        janela_novo_registro['componente_temp'].update('')
                        sg.popup(f"Componente '{componente_temp}' adicionado à lista.")
            
            if evento_novo == "Remover Componente":
                    componente_temp = valores_novo.get('componente_temp')  # Captura o valor do campo de entrada
                    if componente_temp:
                        if componente_temp in componentes_temporarios:
                            componentes_temporarios = remover_componente(componente_temp, componentes_temporarios)
                            janela_novo_registro['lista_componentes'].update(values=componentes_temporarios)
                            sg.popup(f"Componente '{componente_temp}' removido da lista.")
                        else:
                            sg.popup(f"Componente '{componente_temp}' não encontrado na lista.")  # Caso o componente não esteja na lista
                        janela_novo_registro['componente_temp'].update('')  # Limpa o campo após a tentativa de remoção
                    else:
                        sg.popup("Nenhum componente foi selecionado para remoção.")  # Mensagem se nenhum componente estiver selecionado
            
            if evento_novo == "Criar":
                # Validação básica de campos obrigatórios
                if not valores_novo['qrcode_copo'] or not valores_novo['qrcode_placa']:
                    sg.popup('Preencha QRCode do Copo e QRCode da Placa campos obrigatórios.')
                    continue

                # Validação de duplicidade das etiquetas com checagem de data
                cursor.execute('''
                    SELECT COUNT(*) FROM registros 
                    WHERE (qrcode_copo = ? AND input_time = ?) OR (qrcode_placa = ? AND input_time = ?)
                ''', (valores_novo['qrcode_copo'], datetime.now().strftime("%d-%m-%Y %H:%M:%S"), valores_novo['qrcode_placa'], datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
                
                resultado = cursor.fetchone()

                if resultado[0] > 0:
                    sg.popup('Etiqueta Copo ou Etiqueta Placa já existente no banco de dados com uma data igual. Por favor, use valores únicos ou uma data diferente.')
                    conn.close()
                    continue

                # Define o debug_time e repair_time se necessário
                debug_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S") if valores_novo['debug'] else ''
                repair_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S") if valores_novo['reparadora'] else ''
                
                # Inserindo o novo registro no banco de dados
                try:
                    cursor.execute('''
                        INSERT INTO registros (
                            qrcode_copo, 
                            qrcode_placa, 
                            input_time, 
                            testador_id, 
                            debug_id, 
                            debug_time, 
                            reparadora_id, 
                            repair_time, 
                            componentes,
                            observacao
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        valores_novo['qrcode_copo'],
                        valores_novo['qrcode_placa'],
                        datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        int(valores_novo['testador'].split(' ')[0]) if valores_novo['testador'] else None,
                        int(valores_novo['debug'].split(' ')[0]) if valores_novo['debug'] else None,
                        debug_time,
                        int(valores_novo['reparadora'].split(' ')[0]) if valores_novo['reparadora'] else None,
                        repair_time,
                        ','.join(componentes_temporarios),
                        valores_novo['observacao']
                    ))
                    conn.commit()
                    sg.popup('Registro criado com sucesso!')

                    # Limpar os campos após criação do registro
                    janela_novo_registro['qrcode_copo'].update('')
                    janela_novo_registro['qrcode_placa'].update('')
                    janela_novo_registro['testador'].update('')
                    janela_novo_registro['debug'].update('')
                    janela_novo_registro['reparadora'].update('')
                    janela_novo_registro['componente_temp'].update('')
                    janela_novo_registro['lista_componentes'].update(values=[])
                    janela_novo_registro['observacao'].update('')

                    # Atualizar a listbox de registros no Menu
                    registros = get_registros()  # Obtém os registros ordenados
                    janela['registros'].update(values=[f'{registro[0]} - {registro[1]}' for registro in registros])

                except sqlite3.Error as e:
                    sg.popup(f'Ocorreu um erro ao adicionar o registro: {e}')
                finally:
                    conn.close()
        
    if evento == "Buscar":
        etiqueta = valores['buscar_etiqueta']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM registros WHERE qrcode_copo=? OR qrcode_placa=? ORDER BY input_time DESC LIMIT 1', (etiqueta, etiqueta))
        dados = cursor.fetchone()
        conn.close()
        
        if dados is None:
            sg.popup('Registro não encontrado!')  # Exibe um popup se nenhum registro for encontrado
        
        if dados:
            dados_dict = {
                'qrcode_copo': dados[1],
                'qrcode_placa': dados[2],
                'input_time': dados[3],
                'testador': f"{dados[4]} - {get_list_from_db('testadores')[dados[4]-1].split(' - ')[1]}" if dados[4] else '',
                'debug': f"{dados[5]} - {get_list_from_db('debuggers')[dados[5]-1].split(' - ')[1]}" if dados[5] else '',
                'debug_time': dados[6],
                'reparadora': f"{dados[7]} - {get_list_from_db('reparadoras')[dados[7]-1].split(' - ')[1]}" if dados[7] else '',
                'repair_time': dados[8],
                'observacao': dados[10]
            }
            
            # Inicializa a variável 'componentes_temporarios'
            componentes_temporarios = dados[9].split(',') if dados[9] else []
            dados_dict['lista_componentes'] = componentes_temporarios
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
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO testadores (nome) VALUES (?)', (nome_testador.strip(),))
                        conn.commit()
                        conn.close()
                        janela_atualizar_registro['testador'].update(values=get_list_from_db('testadores'))
                
                if evento_update == "Adicionar Debug":
                    nome_debugger = sg.popup_get_text("Nome do Debugger:")
                    if nome_debugger:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO debuggers (nome) VALUES (?)', (nome_debugger.strip(),))
                        conn.commit()
                        conn.close()
                        janela_atualizar_registro['debug'].update(values=get_list_from_db('debuggers'))
                
                if evento_update == "Adicionar Reparadora":
                    nome_reparadora = sg.popup_get_text("Nome da Reparadora:")
                    if nome_reparadora:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO reparadoras (nome) VALUES (?)', (nome_reparadora.strip(),))
                        conn.commit()
                        conn.close()
                        janela_atualizar_registro['reparadora'].update(values=get_list_from_db('reparadoras'))
                
                if evento_update == "Adicionar Componente":
                    componente_temp = valores_update['componente_temp']
                    if not componente_temp.strip():  # strip() remove espaços em branco no início e no fim
                        sg.popup("O campo de componente está vazio. Por favor, insira um valor válido.")
                    if componente_temp:
                        componentes_temporarios = adicionar_componente(componente_temp, componentes_temporarios)
                        janela_atualizar_registro['lista_componentes'].update(values=componentes_temporarios)
                        janela_atualizar_registro['componente_temp'].update('')
                        sg.popup(f"Componente '{componente_temp}' adicionado da lista.")
                        
                if evento_update == "Remover Componente":
                    componente_temp = valores_update.get('componente_temp')  # Captura o valor do campo de entrada
                    if componente_temp:
                        if componente_temp in componentes_temporarios:
                            componentes_temporarios = remover_componente(componente_temp, componentes_temporarios)
                            janela_atualizar_registro['lista_componentes'].update(values=componentes_temporarios)
                            sg.popup(f"Componente '{componente_temp}' removido da lista.")
                        else:
                            sg.popup(f"Componente '{componente_temp}' não encontrado na lista.")  # Caso o componente não esteja na lista
                        janela_atualizar_registro['componente_temp'].update('')  # Limpa o campo após a tentativa de remoção
                    else:
                        sg.popup("Nenhum componente foi preenchido para remoção.")  # Mensagem se nenhum componente estiver selecionado   
                
                if evento_update == "Atualizar":
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    # Obter o registro atual para comparação
                    cursor.execute('SELECT * FROM registros WHERE id = ?', (dados[0],))
                    registro_atual = cursor.fetchone()

                    # Verifica e atualiza debug_time apenas se estiver vazio
                    debug_time = registro_atual[6] if registro_atual[6] else (datetime.now().strftime("%d-%m-%Y %H:%M:%S") if valores_update['debug'] else '')

                    # Verifica e atualiza repair_time apenas se estiver vazio
                    repair_time = registro_atual[8] if registro_atual[8] else (datetime.now().strftime("%d-%m-%Y %H:%M:%S") if valores_update['reparadora'] else '')

                    # Obter nomes de testador, debugger e reparadora
                    testador_nome = None
                    if valores_update['testador']:
                        testador_id = int(valores_update['testador'].split(' ')[0])
                        cursor.execute("SELECT nome FROM testadores WHERE id = ?", (testador_id,))
                        resultado = cursor.fetchone()
                        testador_nome = resultado[0] if resultado else None

                    debug_nome = None
                    if valores_update['debug']:
                        debug_id = int(valores_update['debug'].split(' ')[0])
                        cursor.execute("SELECT nome FROM debuggers WHERE id = ?", (debug_id,))
                        resultado = cursor.fetchone()
                        debug_nome = resultado[0] if resultado else None

                    reparadora_nome = None
                    if valores_update['reparadora']:
                        reparadora_id = int(valores_update['reparadora'].split(' ')[0])
                        cursor.execute("SELECT nome FROM reparadoras WHERE id = ?", (reparadora_id,))
                        resultado = cursor.fetchone()
                        reparadora_nome = resultado[0] if resultado else None

                    # Comparar e registrar no histórico se houver mudanças
                    if (valores_update['componente_temp'] != registro_atual[1]) or (debug_time and debug_time != registro_atual[6]) or (repair_time and repair_time != registro_atual[8]):
                        cursor.execute(
                            'INSERT INTO historico (registro_id, qrcode_copo, qrcode_placa, input_time, testador_nome, debug_nome, debug_time, reparadora_nome, repair_time, componentes, observacao, data_alteracao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            (dados[0],  # registro_id
                            valores_update['qrcode_copo'],
                            valores_update['qrcode_placa'],
                            valores_update['input_time'],
                            testador_nome,  # Nome do testador
                            debug_nome,  # Nome do debugger
                            debug_time,
                            reparadora_nome,  # Nome da reparadora
                            repair_time,
                            ','.join(componentes_temporarios),
                            valores_update['observacao'],
                            datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # data_alteracao
                            )
                        )

                    # Atualizar o registro no banco de dados
                    cursor.execute('''
                        UPDATE registros SET
                        qrcode_copo = ?, 
                        qrcode_placa = ?, 
                        testador_id = ?, 
                        debug_id = ?, 
                        debug_time = ?, 
                        reparadora_id = ?, 
                        repair_time = ?, 
                        componentes = ?,
                        observacao = ?
                        WHERE id = ?
                    ''', (
                        valores_update['qrcode_copo'],
                        valores_update['qrcode_placa'],
                        int(valores_update['testador'].split(' ')[0]) if valores_update['testador'] else None,
                        int(valores_update['debug'].split(' ')[0]) if valores_update['debug'] else None,
                        debug_time,
                        int(valores_update['reparadora'].split(' ')[0]) if valores_update['reparadora'] else None,
                        repair_time,
                        ','.join(componentes_temporarios),
                        valores_update['observacao'],
                        dados[0]
                    ))

                    conn.commit()
                    conn.close()

                    sg.popup('Registro atualizado com sucesso!')
                    janela_atualizar_registro.close()
                    janela.un_hide()

                    # Atualizar a listbox de registros no Menu
                    registros = get_registros()  # Obtém os registros ordenados
                    janela['registros'].update(values=[f'{registro[0]} - {registro[1]}' for registro in registros])
                    break
                
                if evento_update == "Excluir":
                    confirmar_exclusao = sg.popup_yes_no('Deseja realmente excluir este registro?', title='Confirmação de Exclusão')
                    
                    if confirmar_exclusao == 'Yes':
                        # Realizar a exclusão
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM registros WHERE id=?', (dados[0],))
                        conn.commit()
                        conn.close()
                        sg.popup('Registro excluído com sucesso!')

                        # Fecha a janela de atualização e exibe a janela principal
                        janela_atualizar_registro.close()
                        janela.un_hide()
                    else:
                        # Se o usuário escolheu "No", apenas fecha o popup de confirmação e retorna
                        sg.popup('Exclusão cancelada.')
                        
                        # Manter a janela de atualização aberta e retornar ao loop principal sem fechar
                        continue  # Continua o loop principal sem fechar ou congelar a janela

                    # Atualizar a listbox de registros no Menu
                    registros = get_registros()  # Obtém os registros ordenados
                    janela['registros'].update(values=[f'{registro[0]} - {registro[1]}' for registro in registros])
                    break
                
                if evento_update == "Ver Histórico":
                    mostrar_historico(dados[0])  # Passe o ID do registro
                    
                if evento_update == 'Exportar Modificacoes':
                        export_to_csvat()

janela.close()