# **ContentFlow - Automação de Vídeos com IA**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![AI Powered](https://img.shields.io/badge/AI%20Powered-Gemini%20%7C%20TTS%20%7C%20Whisper-orange.svg)

Um pipeline de automação para criar vídeos curtos em múltiplos idiomas, utilizando IA para geração de roteiros, clonagem de voz e legendas sincronizadas.

---

## **Índice**

- [Sobre o Projeto](#sobre-o-projeto)
- [Principais Funcionalidades](#principais-funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação e Configuração](#instalação-e-configuração)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Como Usar](#como-usar)
- [Configurando o Conteúdo](#configurando-o-conteúdo)
- [Licença](#licença)
- [Autor](#autor)

---

## **Sobre o Projeto**

O ContentFlow nasceu da necessidade de otimizar e escalar a produção de conteúdo em vídeo para redes sociais. Criar vídeos manualmente, especialmente para múltiplos canais e em diferentes idiomas, é um processo lento, repetitivo e caro.

Este projeto resolve esse problema automatizando todo o fluxo de trabalho: desde a concepção da ideia até a renderização do vídeo final. Utilizando um conjunto de ferramentas de IA de ponta, o ContentFlow transforma simples temas em vídeos curtos e engajantes, prontos para serem publicados.

---

## **Principais Funcionalidades**

- **Geração de Roteiros com IA:** Utiliza a API do Google Gemini para criar roteiros curtos e impactantes a partir de um tema.
- **Suporte Multilíngue:** Gera vídeos em Português, Inglês e Espanhol, traduzindo automaticamente os roteiros.
- **Clonagem de Voz:** Emprega o Coqui TTS (modelo XTTS v2) para clonar vozes a partir de amostras de áudio curtas, dando uma identidade única a cada vídeo.
- **Legendas Sincronizadas:** Usa o OpenAI Whisper para transcrever o áudio gerado e criar legendas perfeitamente sincronizadas com a fala.
- **Montagem Automática:** Orquestra a edição de vídeo com o MoviePy, juntando vídeo de fundo, narração, música, imagem de personagem e as legendas.
- **Altamente Configurável:** Adicionar novos temas, personagens ou mídias é tão simples quanto editar um arquivo de texto ou adicionar um arquivo a uma pasta.

---

## **Tecnologias Utilizadas**

- **Linguagem:** Python 3.9+
- **Edição de Vídeo:** `MoviePy`
- **Geração de Roteiro:** `Google Gemini API`
- **Síntese de Voz (TTS):** `Coqui TTS (XTTS-v2)`
- **Transcrição e Legendas:** `OpenAI Whisper`
- **Tradução:** `Deep-Translator`
- **Machine Learning:** `PyTorch`

---

## **Instalação e Configuração**

Siga estes passos para configurar o ambiente e executar o projeto.

### **1. Pré-requisitos**

- [Python 3.9](https://www.python.org/downloads/) ou superior.
- [Git](https://git-scm.com/downloads/).
- **FFmpeg:** O MoviePy requer o FFmpeg para manipulação de vídeo e áudio. Faça o download no [site oficial](https://ffmpeg.org/download.html) e adicione-o ao PATH do seu sistema.

### **2. Clone o Repositório**

```bash
git clone [https://github.com/](https://github.com/)[SEU_USUARIO_GITHUB]/ContentFlow.git
cd ContentFlow
```
### **3. Crie um Ambiente Virtual**
É uma boa prática isolar as dependências do projeto.

Bash

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
4. Instale as Dependências
Crie um arquivo requirements.txt na raiz do projeto com o seguinte conteúdo:

Plaintext

moviepy
TTS
openai-whisper
google-generativeai
deep-translator
torch
torchaudio
torchvision
python-dotenv
Em seguida, instale todas as bibliotecas com um único comando:

Bash
```
pip install -r requirements.txt
```
### **5. Configure as Variáveis de Ambiente**
Crie um arquivo chamado .env na raiz do projeto e adicione sua chave da API do Google Gemini.

GOOGLE_API_KEY="SUA_CHAVE_API_AQUI"
Estrutura de Pastas
Para que o script funcione corretamente, organize seus arquivos da seguinte maneira:
```
ContentFlow/
│
├── criar_video.py
├── temas_filosofia.txt
├── temas_desenvolvimento_pessoal.txt
├── temas_curiosidades.txt
├── .env
├── requirements.txt
├── README.md
│
├── musicas/
│   └── musica_fundo_1.mp3
│
├── videos_parkour/
│   └── video_bg_1.mp4
│
├── personagens_img/
│   └── ModeloRick.png
│
└── amostras_voz/
    └── amostra_Rick.wav
```
Como Usar
Com o ambiente virtual ativado e as pastas configuradas, execute o script principal:

Bash
```
python criar_video.py

```
O script irá gerar todos os vídeos e salvá-los na pasta videos_gerados, que será criada automaticamente.

Configurando o Conteúdo
Adicionar Novos Temas
Basta adicionar uma nova linha em qualquer um dos arquivos temas_*.txt.

Adicionar Novos Personagens
Coloque a imagem do personagem na pasta personagens_img/.

Coloque uma amostra da voz (arquivo .wav de 5-15 segundos) na pasta amostras_voz/.

Abra o arquivo criar_video.py e adicione um novo dicionário à lista PERSONAGENS, seguindo o modelo dos outros.

Licença
Este projeto está sob a licença MIT.

Autor
Alfredo Henrique Silveira Bezerra dos Santos

GitHub: [https://github.com/AlfredoBsantos/ProjetoYoutubeDark](https://github.com/AlfredoBsantos/ProjetoYoutubeDark)

LinkedIn: [www.linkedin.com/in/alfredo-santos-08230121a](www.linkedin.com/in/alfredo-santos-08230121a)
