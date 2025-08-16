# Fábrica de Conteúdo com IA (Projeto Dark)

## 📖 Sobre o Projeto

Este projeto é uma automação completa para a criação de vídeos curtos no estilo "diálogo filosófico/divertido", projetado para operar uma rede de até 9 canais no YouTube e TikTok em 3 idiomas diferentes (Português, Inglês e Espanhol).

A automação cobre todo o ciclo de vida do conteúdo, desde a geração da ideia até a preparação para o upload, utilizando uma combinação de IAs locais e APIs externas. O projeto nasceu de uma conversa para explorar alternativas de carreira e se transformou em uma poderosa ferramenta de criação de conteúdo em massa.

---

## ✨ Funcionalidades Principais

* **Geração de Ideias Híbrida:** Utiliza a API do Reddit para buscar tópicos de debate em alta e uma IA local (Ollama com Gemma/Llama) para transformar esses tópicos em temas de vídeo virais.
* **Controle Remoto via Telegram:** Um bot "maestro" permite adicionar novas ideias, iniciar a geração de ideias e comandar a produção de remessas de vídeo, tudo remotamente.
* **Roteiros com IA:** Gera diálogos únicos e dinâmicos entre duplas de personagens, com personalidades e estilos de fala customizados através de prompts otimizados.
* **Clonagem de Voz Multilíngue:** Utiliza o Coqui TTS (modelo XTTS v2) e modelos RVC (via Applio) para clonar vozes a partir de amostras de áudio, gerando narrações em Português, Inglês e Espanhol com alta fidelidade.
* **Edição de Vídeo Automatizada:** Monta o vídeo final usando `MoviePy`, combinando:
    * Vídeo de fundo (gameplay de parkour).
    * Música de fundo.
    * Diálogo com as vozes clonadas.
    * Imagem do personagem que está falando, aparecendo dinamicamente.
    * Legendas sincronizadas palavra por palavra, geradas com `Whisper`.
* **Fila de Produção Inteligente:** Gerencia as ideias de vídeo em uma fila para garantir que o conteúdo não seja repetido, movendo temas usados para um arquivo de "arquivo morto".
* **Upload Automatizado (Opcional):** Um robô de upload com Selenium capaz de agendar os vídeos diretamente no YouTube Studio.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **IA de Roteiro:** Ollama (rodando o modelo `gemma3` ou `llama3:8b` localmente)
* **IA de Voz (TTS):** Coqui TTS (modelo XTTS v2) & RVC (via Applio)
* **IA de Legendas (STT):** OpenAI Whisper (modelo `base`)
* **Edição de Vídeo:** MoviePy
* **Automação de Navegador:** Selenium
* **APIs Externas:** PRAW (API do Reddit), Google Translator (via `deep-translator`)
* **Bot:** `python-telegram-bot`
* **Gerenciamento de Ambiente:** `venv` (Ambiente Virtual Python)

---

## 📂 Estrutura do Projeto

```
ProjetoYoutubeDark/
├── assets/
│   ├── background_music/
│   ├── background_videos/
│   ├── character_images/
│   ├── themes/
│   └── voice_samples/
├── credentials/
│   ├── client_secrets.json
│   └── token_....pickle
├── output/
│   └── generated_videos/
├── src/
│   ├── bot_telegram.py
│   ├── criar_video.py
│   ├── gerador_de_ideias.py
│   └── uploader_youtube.py
├── temp/
│   └── temp_audio/
├── .gitignore
├── config.py
├── README.md
└── venv/

```
---

## 🚀 Como Usar a Fábrica

**Pré-requisitos:**
* Python 3.11
* FFMPEG instalado e no PATH do sistema.
* Ollama instalado e com um modelo (ex: `gemma3`) baixado.
* (Opcional para RVC) Applio instalado e com os modelos de voz na pasta `logs`.
* (Opcional para Upload) Google Chrome e atalho de depuração configurado.

**Workflow de Produção:**

1.  **Ligue os Motores:** Certifique-se de que o aplicativo **Ollama** e, se for usar vozes RVC, o **Applio** estejam rodando em segundo plano.
2.  **Inicie o Painel de Controle:** Abra um terminal, ative o ambiente virtual (`.\venv\Scripts\activate`) e rode o bot maestro:
    ```powershell
    python src/bot_telegram.py
    ```
3.  **Comande pelo Telegram:**
    * **`/gerarideias`**: Para buscar novos temas no Reddit e salvá-los na fila.
    * **`/adicionarideia`**: Para adicionar uma ideia manualmente.
    * **`/criarteste`**: Para gerar 1 vídeo de teste e recebê-lo no Telegram.
    * **`/criarremessa`**: Para iniciar a produção completa de 9 vídeos e recebê-los no Telegram.
4.  **Distribua o Conteúdo:** Faça o upload manual dos vídeos gerados na pasta `output/generated_videos`, usando os arquivos `.txt` de metadados como guia.

---

### requirements.txt

Para facilitar a reinstalação do projeto no futuro, crie um arquivo `requirements.txt` na raiz do projeto com o comando:
`pip freeze > requirements.txt`

Para instalar todas as dependências de uma vez, use:
`pip install -r requirements.txt`
