from flask import Flask, request, jsonify, render_template, session, redirect
from datetime import datetime
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
    temas = df['Tema'].unique()
    top5 = get_top5()
    return render_template('index.html', temas=temas, top5=top5)

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    tema = request.form['tema']
    usuario = request.form['usuario']
    session['tema'] = tema
    session['usuario'] = usuario
    session['score'] = 0
    session['pulos'] = 3
    session['consultas_l2'] = 1
    session['cartas'] = 1
    session['consultas_artigo'] = 1
    session['answered_questions'] = []
    return render_template('quiz.html', tema=tema, usuario=usuario)

@app.route('/get_question', methods=['POST'])
def get_question():
    tema = session.get('tema')
    perguntas_tema = df[df['Tema'] == tema]

    if perguntas_tema.empty:
        return jsonify({'error': 'Nenhuma pergunta encontrada para esse tema.'}), 404

    answered_questions = session.get('answered_questions', [])
    perguntas_restantes = perguntas_tema[~perguntas_tema.index.isin(answered_questions)]

    if perguntas_restantes.empty:
        save_score()
        return jsonify({'success': 'Você ganhou! Todas as perguntas foram respondidas.'}), 200

    pergunta = perguntas_restantes.sample(n=1).iloc[0]
    session['answered_questions'].append(int(pergunta.name))
    opcoes = [
        pergunta['Resposta Correta'],
        pergunta['Resposta Errada 1'],
        pergunta['Resposta Errada 2'],
        pergunta['Resposta Errada 3']
    ]
    random.shuffle(opcoes)
    session['correct_answer'] = pergunta['Resposta Correta']
    session['artigo'] = pergunta['Material de consulta'] if not pd.isna(pergunta['Material de consulta']) else None
    session['current_question'] = pergunta['Pergunta']
    session['current_options'] = opcoes

    # Total de perguntas
    total_perguntas = len(perguntas_tema)
    # Número da pergunta atual
    pergunta_numero = len(session['answered_questions'])

    return jsonify({
        'pergunta': pergunta['Pergunta'],
        'opcoes': opcoes,
        'tema': tema,
        'usuario': session.get('usuario'),
        'score': session.get('score'),
        'pulos': session.get('pulos'),
        'consultas_l2': session.get('consultas_l2'),
        'cartas': session.get('cartas'),
        'consultas_artigo': session.get('consultas_artigo'),
        'artigo': session['artigo'],
        'total_perguntas': total_perguntas,
        'pergunta_numero': pergunta_numero
    })

@app.route('/check_answer', methods=['POST'])
def check_answer():
    resposta = request.form['resposta']
    correct_answer = session.get('correct_answer')
    current_question = session.get('current_question')
    if resposta == correct_answer:
        session['score'] += 1
        return jsonify({'correct': True})
    else:
        save_score()
        return jsonify({'correct': False, 'score': session.get('score'), 'question': current_question, 'correct_answer': correct_answer})


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
        cartas = ['0', '1', '2', '3']
        carta_escolhida = random.choice(cartas)

        opcoes = session.get('current_options')
        correct_answer = session.get('correct_answer')
        respostas_erradas = [opcao for opcao in opcoes if opcao != correct_answer]

        if carta_escolhida == '0':
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

        carta_imagem = f"static/images/card{carta_escolhida}.png"

        return jsonify({'success': True, 'carta': carta_escolhida, 'carta_imagem': carta_imagem, 'opcoes': novas_opcoes, 'cartas': session['cartas'], 'pergunta': session['current_question']})
    return jsonify({'success': False})


@app.route('/use_article', methods=['POST'])
def use_article():
    if session['consultas_artigo'] > 0:
        session['consultas_artigo'] -= 1
        artigo = session.get('artigo')
        if artigo:
            return jsonify({'success': True, 'artigo': artigo, 'consultas_artigo': session['consultas_artigo']})
        else:
            return jsonify({'success': False, 'message': 'Nenhum artigo disponível para esta questão.'})
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
    tema = session.get('tema')
    quiz_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('data.json', 'r') as f:
        data = json.load(f)
    data.append({'usuario': usuario, 'score': score, 'quiz': tema, 'date': quiz_date})
    with open('data.json', 'w') as f:
        json.dump(data, f)

@app.route('/reset', methods=['POST'])
def reset():
    return redirect('/')

@app.route('/get_top5', methods=['GET'])
def get_top5_route():
    tema = request.args.get('tema')
    if not tema:
        return jsonify([])

    top5 = get_top5(tema)
    return jsonify(top5)


def get_top5(tema=None):
    with open('data.json', 'r') as f:
        data = json.load(f)

    if tema:
        data = [item for item in data if item['quiz'] == tema]

    sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)[:5]
    return sorted_data


if __name__ == '__main__':
    app.run(debug=True)