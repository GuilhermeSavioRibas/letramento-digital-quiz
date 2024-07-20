from flask import Flask, request, jsonify, render_template, session, redirect
import pandas as pd
import random
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Carregar a planilha
df = pd.read_excel('perguntas.xlsx')
df.columns = df.columns.str.strip()

# Verificar se o arquivo JSON existe, caso contrário, criar um novo
if not os.path.exists('data.json'):
    with open('data.json', 'w') as f:
        json.dump([], f)

@app.route('/')
def index():
    empresas = df['Empresa'].unique()
    top5 = get_top5()
    return render_template('index.html', empresas=empresas, top5=top5)

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    empresa = request.form['empresa']
    usuario = request.form['usuario']
    session['empresa'] = empresa
    session['usuario'] = usuario
    session['score'] = 0
    session['pulos'] = 3
    session['consultas_l2'] = 1
    session['cartas'] = 1
    session['consultas_artigo'] = 1
    session['answered_questions'] = []
    return render_template('quiz.html', empresa=empresa, usuario=usuario)

@app.route('/get_question', methods=['POST'])
def get_question():
    empresa = session.get('empresa')
    perguntas_empresa = df[df['Empresa'] == empresa]

    # Adicione logs para depuração
    print(f"Empresa: {empresa}")
    print(f"Perguntas disponíveis: {len(perguntas_empresa)}")

    if perguntas_empresa.empty:
        return jsonify({'error': 'Nenhuma pergunta encontrada para essa empresa.'}), 404

    # Verificar perguntas não respondidas
    answered_questions = session.get('answered_questions', [])
    perguntas_restantes = perguntas_empresa[~perguntas_empresa.index.isin(answered_questions)]

    if perguntas_restantes.empty:
        save_score()
        return jsonify({'error': 'Você ganhou! Todas as perguntas foram respondidas.'}), 404

    pergunta = perguntas_restantes.sample(n=1).iloc[0]
    session['answered_questions'].append(int(pergunta.name))  # Certifique-se de que o índice é serializável
    opcoes = [
        pergunta['Resposta Correta'],
        pergunta['Resposta Errada 1'],
        pergunta['Resposta Errada 2'],
        pergunta['Resposta Errada 3']
    ]
    random.shuffle(opcoes)
    session['correct_answer'] = pergunta['Resposta Correta']
    session['artigo'] = pergunta['Código do Artigo']
    session['current_question'] = pergunta['Pergunta']
    session['current_options'] = opcoes

    # Adicione logs para depuração
    print(f"Pergunta selecionada: {pergunta['Pergunta']}")
    print(f"Opções: {opcoes}")

    return jsonify({
        'pergunta': pergunta['Pergunta'],
        'opcoes': opcoes,
        'empresa': empresa,
        'usuario': session.get('usuario'),
        'score': session.get('score'),
        'pulos': session.get('pulos'),
        'consultas_l2': session.get('consultas_l2'),
        'cartas': session.get('cartas'),
        'consultas_artigo': session.get('consultas_artigo')
    })

@app.route('/check_answer', methods=['POST'])
def check_answer():
    resposta = request.form['resposta']
    correct_answer = session.get('correct_answer')
    if resposta == correct_answer:
        session['score'] += 1
        return jsonify({'correct': True})
    else:
        save_score()
        return jsonify({'correct': False, 'score': session.get('score')})

@app.route('/use_skip', methods=['POST'])
def use_skip():
    if session['pulos'] > 0:
        session['pulos'] -= 1
        return jsonify({'success': True, 'pulos': session['pulos']})
    return jsonify({'success': False})

@app.route('/use_l2', methods=['POST'])
def use_l2():
    if session['consultas_l2'] > 0:
        session['consultas_l2'] -= 1
        return jsonify({'success': True, 'consultas_l2': session['consultas_l2']})
    return jsonify({'success': False})

@app.route('/use_card', methods=['POST'])
def use_card():
    if session['cartas'] > 0:
        session['cartas'] -= 1
        cartas = ['K', '1', '2', '3']
        carta_escolhida = random.choice(cartas)

        opcoes = session.get('current_options')
        correct_answer = session.get('correct_answer')
        respostas_erradas = [opcao for opcao in opcoes if opcao != correct_answer]

        if carta_escolhida == 'K':
            # Não elimina nenhuma resposta
            pass
        elif carta_escolhida == '1' and len(respostas_erradas) >= 1:
            respostas_erradas = respostas_erradas[:2]
        elif carta_escolhida == '2' and len(respostas_erradas) >= 2:
            respostas_erradas = respostas_erradas[:1]
        elif carta_escolhida == '3':
            respostas_erradas = respostas_erradas[:0]

        novas_opcoes = [correct_answer] + respostas_erradas
        random.shuffle(novas_opcoes)

        session['current_options'] = novas_opcoes

        return jsonify({'success': True, 'carta': carta_escolhida, 'opcoes': novas_opcoes, 'cartas': session['cartas'], 'pergunta': session['current_question']})
    return jsonify({'success': False})

@app.route('/use_article', methods=['POST'])
def use_article():
    if session['consultas_artigo'] > 0:
        session['consultas_artigo'] -= 1
        artigo = session.get('artigo')
        return jsonify({'success': True, 'artigo': artigo, 'consultas_artigo': session['consultas_artigo']})
    return jsonify({'success': False})

@app.route('/get_article', methods=['GET'])
def get_article():
    artigo = session.get('artigo')
    return jsonify({'artigo': artigo})

@app.route('/end_quiz', methods=['POST'])
def end_quiz():
    save_score()
    return redirect('/')

def get_top5():
    with open('data.json', 'r') as f:
        data = json.load(f)
    sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)[:5]
    return sorted_data

def save_score():
    usuario = session.get('usuario')
    score = session.get('score')
    with open('data.json', 'r') as f:
        data = json.load(f)
    data.append({'usuario': usuario, 'score': score})
    with open('data.json', 'w') as f:
        json.dump(data, f)

@app.route('/reset', methods=['POST'])
def reset():
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
