# Service Desk Quiz

Um projeto de quiz baseado em serviço de suporte, desenvolvido para testar e aprimorar conhecimentos sobre o serviço de atendimento. O quiz é uma aplicação web que utiliza HTML, CSS, JavaScript e Python com Flask para criar uma experiência interativa e educativa.

## Descrição

O Service Desk Quiz é uma aplicação web simples onde os usuários podem responder a perguntas sobre suporte técnico. O sistema faz perguntas aleatórias a partir de um banco de dados em Excel e exibe uma pontuação final com base nas respostas corretas. 

https://service-desk-quiz.onrender.com/

## Funcionalidades

- **Perguntas Aleatórias:** O quiz puxa perguntas aleatórias de um arquivo Excel.
- **Pontuação:** O usuário ganha 1 ponto por resposta correta.
- **Resolução de Respostas Incorretas:** Se o usuário errar uma resposta, o jogo termina e a pontuação é exibida.
- **Registro de Pontuação:** As pontuações são salvas em um relatório para análise futura.
- **Evitar Perguntas Repetidas:** As perguntas não se repetem durante o mesmo jogo.

## Tecnologias Utilizadas

- **HTML** para estruturação da página.
- **CSS** para estilização.
- **JavaScript** para lógica do quiz e manipulação de dados.
- **Excel** como fonte de dados para as perguntas.
- **Flask** para o backend da aplicação.
- **pandas** para manipulação dos dados do Excel.

![image](https://github.com/user-attachments/assets/cfd3c76e-14bd-4bcc-93ee-9b9f4f1bf070)

![image](https://github.com/user-attachments/assets/441792ed-73f2-47c0-89a5-4209b012c841)

## Como Rodar o Projeto

1. **Clone o Repositório:**
   ```bash
   git clone https://github.com/GuilhermeSavioRibas/Service-Desk-Quiz.git

2. **Navegue até o Diretório do Projeto:**

    ```bash
    cd Service-Desk-Quiz

3. **Configure o Arquivo de Perguntas:**

    Certifique-se de que o arquivo perguntas.xlsx está no mesmo diretório que o seu script app.py.

4. **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    
5. **Execute o Servidor Flask:**
    ```bash
    python app.py

6. **Abra o servidor criado em um navegador web**
    Exemplo: http://127.0.0.1:5000


## Contato

Para mais informações, entre em contato com:

* Nome: Guilherme Savio Ribas
* E-mail: guilherme.savio@gmail.com
* GitHub: GuilhermeSavioRibas
