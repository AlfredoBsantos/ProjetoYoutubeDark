import os
import random
import re
from moviepy.editor import *
from moviepy.audio.fx.all import audio_loop
from TTS.api import TTS
import google.generativeai as genai
import torch
import whisper
from deep_translator import GoogleTranslator # NOVO IMPORT PARA TRADUÇÃO

# --- 1. CONFIGURAÇÃO INICIAL ---
GOOGLE_API_KEY = 'AIzaSyC-teU44gErrUY1xWpKd5VZD00m9jbynI8' 
genai.configure(api_key=GOOGLE_API_KEY)

# --- CONFIGURAÇÃO DOS CANAIS ---
# Estrutura principal que define cada um dos seus 3 tipos de canal
CANAIS_CONFIG = [
    {
        "tema_categoria": "Filosofia",
        "arquivo_temas": "temas_filosofia.txt"
    },
    {
        "tema_categoria": "Desenvolvimento Pessoal",
        "arquivo_temas": "temas_desenvolvimento_pessoal.txt"
    },
    {
        "tema_categoria": "Curiosidades",
        "arquivo_temas": "temas_curiosidades.txt"
    }
]

# --- CONFIGURAÇÃO DE PERSONAGENS E PASTAS ---
PERSONAGENS = [
    {
        "nome": "Braian Griffin",
        "arquivo_voz": "amostra_BraianGriffin.wav",
        "arquivo_imagem": "personagens_img/ModeloBraianGriffin.png"
    },
    {
        "nome": "Clancy Gospel",
        "arquivo_voz": "amostra_ClancyGospel.wav",
        "arquivo_imagem": "personagens_img/modeloClancyGospel.png"
    },
    {
        "nome": "Mae Gospel",
        "arquivo_voz": "amostra_MaeGospel.wav",
        "arquivo_imagem": "personagens_img/ModeloMaeGospel.png"
    },
    {
        "nome": "Mob",
        "arquivo_voz": "amostra_mob.wav",
        "arquivo_imagem": "personagens_img/ModeloMob.png"
    },
    {
        "nome": "Mordecai",
        "arquivo_voz": "amostra_Mordecai.wav",
        "arquivo_imagem": "personagens_img/ModeloMordecai.png"
    },
    {
        "nome": "Morty",
        "arquivo_voz": "amostra_Morty.wav",
        "arquivo_imagem": "personagens_img/ModeloMorty.png"
    },
    {
        "nome": "Peter Griffin",
        "arquivo_voz": "amostra_PiterGriffin.wav",
        "arquivo_imagem": "personagens_img/ModeloPitterGriffin.png"
    },
    {
        "nome": "Reigen Arataka",
        "arquivo_voz": "amostra_reigen.wav", # Assumindo que você tem o arquivo da voz original do Reigen
        "arquivo_imagem": "personagens_img/ModeloReigen.png"
    },
    {
        "nome": "Rick Sanchez",
        "arquivo_voz": "amostra_Rick.wav",
        "arquivo_imagem": "personagens_img/ModeloRick.png"
    },
    {
        "nome": "Rigby",
        "arquivo_voz": "amostra_Rigby.wav",
        "arquivo_imagem": "personagens_img/ModeloRigby.png"
    },
]

PASTA_VIDEOS = "videos_parkour"
PASTA_MUSICAS = "musicas"
PASTA_SAIDA = "videos_gerados"
PASTA_IMAGENS_PERSONAGENS = "personagens_img"

os.makedirs(PASTA_SAIDA, exist_ok=True)
os.makedirs(PASTA_IMAGENS_PERSONAGENS, exist_ok=True)


# --- 2. FUNÇÕES AUXILIARES ---

def get_random_file(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files: raise ValueError(f"A pasta está vazia: {folder_path}")
    return os.path.join(folder_path, random.choice(files))

def get_random_theme(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        themes = f.readlines()
    if not themes: raise ValueError(f"O arquivo de temas está vazio: {file_path}")
    return random.choice(themes).strip()

def generate_script(theme):
    print(f"\nGerando roteiro para o tema: {theme}")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Crie um monólogo curto e impactante de até 45 segundos sobre o seguinte tema: '{theme}'. Use um tom filosófico, questionador e um pouco cético. O texto deve ser em português do Brasil."
    response = model.generate_content(prompt)
    print("Roteiro gerado com sucesso!")
    return response.text

def translate_script(text, target_language):
    """Traduz o texto para o idioma alvo."""
    if target_language == 'pt':
        return text
    print(f"Traduzindo roteiro para o idioma: {target_language}...")
    try:
        translated_text = GoogleTranslator(source='auto', target=target_language).translate(text)
        print("Tradução concluída.")
        return translated_text
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return text # Retorna o texto original em caso de falha

def generate_audio(script_text, sample_voice_path, language, output_path):
    print(f"Gerando áudio em '{language}' com a voz de referência: {sample_voice_path}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)
    tts.tts_to_file(text=script_text, file_path=output_path, speaker_wav=sample_voice_path, language=language)
    print(f"Áudio clonado salvo em: {output_path}")

def generate_synced_captions(audio_path):
    print("Carregando modelo Whisper...")
    model = whisper.load_model("base")
    print("Transcrevendo áudio para gerar timestamps...")
    result = model.transcribe(audio_path, word_timestamps=False)
    print("Legendas e timestamps gerados.")
    return result['segments']


# --- 3. FUNÇÃO PRINCIPAL DE MONTAGEM ---
# Agora esta função recebe todos os parâmetros que precisa
def create_video(tema_categoria, tema_escolhido, roteiro, idioma):
    """Função que orquestra a criação de UM vídeo específico."""
    try:
        print(f"\n--- INICIANDO CRIAÇÃO DO VÍDEO ---")
        print(f"| Categoria: {tema_categoria}")
        print(f"| Idioma: {idioma.upper()}")
        
        # Passo 1: Personagem e Tradução
        personagem_escolhido = random.choice(PERSONAGENS)
        print(f"| Personagem: {personagem_escolhido['nome']}")
        
        roteiro_traduzido = translate_script(roteiro, idioma)
        
        # Passo 2: Gerar Mídia
        caminho_audio_narracao = os.path.join(PASTA_SAIDA, f"narracao_{idioma}.wav")
        generate_audio(roteiro_traduzido, personagem_escolhido['arquivo_voz'], idioma, caminho_audio_narracao)
        
        segments = generate_synced_captions(caminho_audio_narracao)
        caminho_video_bg = get_random_file(PASTA_VIDEOS)
        caminho_musica_bg = get_random_file(PASTA_MUSICAS)
        
        # Passo 3: Montagem do vídeo
        print("Iniciando montagem do vídeo...")
        video_clip = VideoFileClip(caminho_video_bg)
        narracao_clip = AudioFileClip(caminho_audio_narracao)
        musica_clip = AudioFileClip(caminho_musica_bg).volumex(0.1)

        video_clip = video_clip.subclip(0, narracao_clip.duration)
        final_music = audio_loop(musica_clip, duration=narracao_clip.duration)
        audio_final = CompositeAudioClip([narracao_clip, final_music])
        video_com_audio = video_clip.set_audio(audio_final)

        imagem_personagem_clip = (ImageClip(personagem_escolhido['arquivo_imagem'])
                                  .set_duration(video_com_audio.duration)
                                  .resize(height=video_com_audio.h * 0.25)
                                  .set_position(("right", "top")))

        caption_clips = []
        for segment in segments:
            start_time, end_time, text = segment['start'], segment['end'], segment['text'].strip().upper()
            caption = TextClip(text, fontsize=32, color='yellow', font='Calibri-Bold', stroke_color='black', stroke_width=2, size=(video_com_audio.w*0.8, None), method='caption')
            caption = caption.set_start(start_time).set_duration(end_time - start_time)
            caption = caption.set_position(('center', 0.75), relative=True)
            caption_clips.append(caption)

        video_final = CompositeVideoClip([video_com_audio, imagem_personagem_clip] + caption_clips)
        
        # Passo 4: Salvar com nome de arquivo organizado
        safe_theme_name = re.sub(r'[\\/*?:"<>|]', '', tema_escolhido)[:20].replace(' ', '_')
        nome_personagem_safe = personagem_escolhido['nome'].replace(' ','')
        nome_arquivo_saida = f"{tema_categoria}_{idioma.upper()}_{nome_personagem_safe}_{safe_theme_name}.mp4"
        caminho_arquivo_saida = os.path.join(PASTA_SAIDA, nome_arquivo_saida)
        
        video_final.write_videofile(caminho_arquivo_saida, codec='libx264', audio_codec='aac')
        
        print(f"✅ VÍDEO GERADO COM SUCESSO: {caminho_arquivo_saida}")

    except Exception as e:
        print(f"❌ Ocorreu um erro ao criar o vídeo para o idioma '{idioma}': {e}")


# --- 4. EXECUTAR A LINHA DE PRODUÇÃO ---
if __name__ == '__main__':
    # Loop principal que orquestra toda a produção
    for canal in CANAIS_CONFIG:
        # Pega um tema para a categoria e gera o roteiro base em Português
        tema_base = get_random_theme(canal['arquivo_temas'])
        roteiro_base_pt = generate_script(tema_base)
        
        # Cria um vídeo para cada idioma usando o mesmo roteiro base
        for idioma in ['pt', 'en', 'es']:
            create_video(
                tema_categoria=canal['tema_categoria'],
                tema_escolhido=tema_base,
                roteiro=roteiro_base_pt,
                idioma=idioma
            )
            
    print("\n🎉 Ciclo de produção concluído! Todos os 9 vídeos foram gerados.")

