# src/criar_video.py

import os
import random
import re
import sys
from moviepy.editor import *
from moviepy.audio.fx.all import audio_loop
from TTS.api import TTS
import ollama
import torch
import whisper
from deep_translator import GoogleTranslator

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# --- CONFIGURAÇÕES ---
CANAIS_CONFIG = config.CANAIS_CONFIG
PERSONAGENS = config.PERSONAGENS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_VIDEOS = os.path.join(BASE_DIR, "assets", "background_videos")
PASTA_MUSICAS = os.path.join(BASE_DIR, "assets", "background_music")
PASTA_IMAGENS_PERSONAGENS = os.path.join(BASE_DIR, "assets", "character_images")
PASTA_TEMAS = os.path.join(BASE_DIR, "assets", "themes")
PASTA_AMOSTRAS_VOZ = os.path.join(BASE_DIR, "assets", "voice_samples")
PASTA_SAIDA = os.path.join(BASE_DIR, "output", "videos_gerados")
PASTA_TEMP_AUDIO = os.path.join(BASE_DIR, "temp", "temp_audio")

os.makedirs(PASTA_SAIDA, exist_ok=True)
os.makedirs(PASTA_TEMP_AUDIO, exist_ok=True)

# --- FUNÇÕES AUXILIARES ---
def get_random_file(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files: raise ValueError(f"A pasta '{folder_path}' está vazia.")
    return os.path.join(folder_path, random.choice(files))

def get_and_archive_next_theme(theme_file_name):
    theme_file_path = os.path.join(PASTA_TEMAS, theme_file_name)
    used_theme_file_path = os.path.join(PASTA_TEMAS, theme_file_name.replace('.txt', '_usados.txt'))
    try:
        with open(theme_file_path, 'r', encoding='utf-8') as f:
            themes = [line for line in f.read().splitlines() if line.strip()]
        if not themes:
            print(f"AVISO: Não há novas ideias no arquivo '{theme_file_name}'.")
            return None
        next_theme = themes.pop(0)
        with open(theme_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(themes))
        with open(used_theme_file_path, 'a', encoding='utf-8') as f:
            f.write(f'{next_theme}\n')
        print(f"Tema selecionado da fila: '{next_theme}'")
        return next_theme
    except FileNotFoundError:
        print(f"AVISO: Arquivo de temas '{theme_file_name}' não encontrado.")
        return None

def generate_dialogue_script(theme, personagem1, personagem2, objetivo_canal):
    print(f"\nGerando diálogo para o tema: '{theme}' entre {personagem1['nome']} e {personagem2['nome']}")
    prompt = f"""
    Aja como os dois personagens a seguir em uma conversa curta e viral para TikTok/YouTube Shorts (máx. 45s).
    ### PERSONAGENS E CONTEXTO
    - Personagem 1: {personagem1['nome']} (personalidade: {personagem1['personalidade']})
    - Personagem 2: {personagem2['nome']} (personalidade: {personagem2['personalidade']})
    - Tema Central: '{theme}'
    - Objetivo do Canal: {objetivo_canal}
    ### GUIA DE ESTILO E ESTRUTURA
    - Formato OBRIGATÓRIO: O roteiro DEVE ser uma alternância de falas, começando sempre com o nome do personagem seguido de dois pontos. Use o primeiro nome (Ex: `Rick:`).
    - Ritmo e Cadência (MAIS IMPORTANTE): A fala deve ser fluida e contínua, com POUCAS E CURTAS pausas. O ritmo é de um vídeo viral, não de um poema.
    - Gancho Imediato: A primeira fala deve ser um gancho magnético.
    - Conclusão de Impacto: A última fala deve ser uma "punchline" memorável.
    ### REGRAS FINAIS DE SAÍDA
    - O resultado deve ser APENAS o diálogo puro, no formato `Nome do Personagem: Fala`.
    - É TERMINANTEMENTE PROIBIDO incluir descrições de ações como (suspira), (arroto), (pausa) ou *olha para o lado*.
    - É PROIBIDO escrever a pontuação por extenso (Ex: "ponto", "vírgula").
    Com base em todas as regras, gere o diálogo.
    """
    try:
        response = ollama.chat(model='gemma3', messages=[{'role': 'user', 'content': prompt}])
        texto_limpo = response['message']['content'].strip()
        print("Diálogo gerado com sucesso!")
        return texto_limpo
    except Exception as e:
        print(f"❌ Erro ao se comunicar com o Ollama: {e}")
        return None

def parse_and_generate_dialogue_audio(script_text, dupla_personagens, language):
    print("Iniciando processamento de áudio do diálogo...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)
    linhas = script_text.strip().split('\n')
    storyboard = []
    caminhos_das_falas = []
    
    for i, linha in enumerate(linhas):
        match = re.match(r'([^:]+):\s*(.*)', linha)
        if not match: continue
        
        nome_personagem_script, texto_fala = match.groups()
        nome_personagem_script = nome_personagem_script.strip()
        personagem_info = None
        for nome_completo, info in dupla_personagens.items():
            if nome_personagem_script.lower() in nome_completo.lower():
                personagem_info = info
                break
        if not personagem_info: 
            print(f"AVISO: Personagem '{nome_personagem_script}' não encontrado. Pulando fala.")
            continue

        print(f"Gerando fala {i+1}/{len(linhas)} para {personagem_info['nome']}...")
        texto_fala_limpo = re.sub(r'[\*()\[\]]', '', texto_fala).replace('.', '...')
        caminho_fala_temp = os.path.join(PASTA_TEMP_AUDIO, f"fala_{i}.wav")
        arquivo_voz_idioma = personagem_info['arquivo_voz'][language]
        caminho_amostra = os.path.join(PASTA_AMOSTRAS_VOZ, arquivo_voz_idioma)
        tts.tts_to_file(text=texto_fala_limpo, file_path=caminho_fala_temp, speaker_wav=caminho_amostra, language=language, speed=1.2)
        
        clip_temp = AudioFileClip(caminho_fala_temp)
        duracao_fala = clip_temp.duration
        clip_temp.close()

        storyboard.append({"personagem": personagem_info, "duracao": duracao_fala})
        caminhos_das_falas.append(caminho_fala_temp)

    clips_de_audio = [AudioFileClip(caminho) for caminho in caminhos_das_falas]
    if not clips_de_audio: raise ValueError("Nenhum clipe de áudio foi gerado.")
    
    audio_final_completo = concatenate_audioclips(clips_de_audio)
    caminho_audio_final = os.path.join(PASTA_SAIDA, f"narracao_completa_{language}.wav")
    audio_final_completo.write_audiofile(caminho_audio_final, codec='pcm_s16le')

    for clip in clips_de_audio: clip.close()
    for caminho in caminhos_das_falas: os.remove(caminho)

    print("Áudio do diálogo completo gerado com sucesso!")
    return caminho_audio_final, storyboard

def generate_word_level_captions(audio_path):
    print("Carregando modelo Whisper para timestamps de palavras...")
    model = whisper.load_model("base")
    print("Transcrevendo áudio para gerar timestamps de palavras...")
    result = model.transcribe(audio_path, word_timestamps=True)
    print("Legendas e timestamps de palavras gerados.")
    return result['segments']

def create_video(tema_categoria, tema_escolhido, dupla_nomes, roteiro_base_pt, idioma):
    try:
        print(f"\n--- INICIANDO CRIAÇÃO DO VÍDEO DE DIÁLOGO ---")
        print(f"| Categoria: {tema_categoria}")
        print(f"| Idioma: {idioma.upper()}")
        
        dupla_personagens = {nome: PERSONAGENS[nome] for nome in dupla_nomes}
        
        roteiro_traduzido = GoogleTranslator(source='auto', target=idioma).translate(roteiro_base_pt) if idioma != 'pt' else roteiro_base_pt
        
        if not roteiro_traduzido: raise ValueError("Roteiro vazio após tradução.")

        caminho_audio_final, storyboard = parse_and_generate_dialogue_audio(roteiro_traduzido, dupla_personagens, idioma)
        
        narracao_clip = AudioFileClip(caminho_audio_final)
        caminho_video_bg = get_random_file(PASTA_VIDEOS)
        caminho_musica_bg = get_random_file(PASTA_MUSICAS)
        
        print("Iniciando montagem do vídeo com camadas dinâmicas...")
        video_clip = VideoFileClip(caminho_video_bg).subclip(0, narracao_clip.duration)
        musica_clip = AudioFileClip(caminho_musica_bg).volumex(0.1)
        final_music = audio_loop(musica_clip, duration=narracao_clip.duration)
        audio_final = CompositeAudioClip([narracao_clip, final_music])
        video_com_audio = video_clip.set_audio(audio_final)

        personagem_clips = []
        tempo_corrente_personagem = 0
        personagem1_info, personagem2_info = list(dupla_personagens.values())
        for fala in storyboard:
            start_time = tempo_corrente_personagem
            personagem_falando = fala['personagem']
            caminho_imagem_personagem = os.path.join(PASTA_IMAGENS_PERSONAGENS, personagem_falando['arquivo_imagem'])
            
            posicao = ("right", "bottom") if personagem_falando['nome'] == personagem1_info['nome'] else ("left", "bottom")
            
            clip_imagem = (ImageClip(caminho_imagem_personagem)
                           .set_start(start_time).set_duration(fala['duracao'])
                           .resize(height=video_com_audio.h * 0.40).set_position(posicao))
            personagem_clips.append(clip_imagem)
            tempo_corrente_personagem += fala['duracao']

        segments = generate_word_level_captions(caminho_audio_final)
        caption_clips = []
        words_to_process = []
        if segments:
            for segment in segments:
                if 'words' in segment:
                    words_to_process.extend(segment['words'])

        word_groups = []
        for i in range(0, len(words_to_process), 2):
            word_groups.append(words_to_process[i:i+2])

        for group in word_groups:
            start_time = group[0]['start']
            end_time = group[-1]['end']
            text = ' '.join(word['word'] for word in group).strip().upper()

            caption = TextClip(text, fontsize=22, color='yellow', font='Arial-Bold', 
                               stroke_color='black', stroke_width=1,
                               method='caption', size=(video_com_audio.w * 0.8, None))
            
            caption = caption.set_start(start_time).set_duration(end_time - start_time).set_position('center')
            caption_clips.append(caption)
        
        video_final = CompositeVideoClip([video_com_audio] + personagem_clips + caption_clips)
        
        safe_theme_name = re.sub(r'[\\/*?:"<>|]', '', tema_escolhido)[:20].replace(' ', '_')
        nome_arquivo_saida = f"{tema_categoria}_{idioma.upper()}_{safe_theme_name}.mp4"
        caminho_arquivo_saida = os.path.join(PASTA_SAIDA, nome_arquivo_saida)
        
        video_final.write_videofile(
    caminho_arquivo_saida, 
    codec='libx264', 
    audio_codec='aac',
    bitrate='2000k',  # Define uma taxa de bits de 2 Mbps (bom para HD em redes sociais)
    preset='medium'   # Um bom equilíbrio entre velocidade de compressão e tamanho
)
        
        print(f"✅ VÍDEO DE DIÁLOGO GERADO COM SUCESSO: {caminho_arquivo_saida}")
        return caminho_arquivo_saida
    except Exception as e:
        print(f"❌ Ocorreu um erro ao criar o vídeo de diálogo: {e}")
        return None

# --- FUNÇÃO PRINCIPAL DE PRODUÇÃO ---
def main(modo_teste=False):
    """Função principal que executa a criação de vídeos e retorna os caminhos dos arquivos."""
    videos_gerados = []
    if modo_teste:
        print("--- RODANDO EM MODO DE TESTE (1 DIÁLOGO) ---")
        canal_teste = CANAIS_CONFIG[0]
        dupla_teste_nomes = canal_teste['dupla']
        personagem1_teste = PERSONAGENS[dupla_teste_nomes[0]]
        personagem2_teste = PERSONAGENS[dupla_teste_nomes[1]]
        tema_teste = get_and_archive_next_theme(canal_teste['arquivo_temas'])
        if tema_teste:
            roteiro_base_pt = generate_dialogue_script(tema_teste, personagem1_teste, personagem2_teste, canal_teste['objetivo'])
            if roteiro_base_pt:
                caminho_video = create_video(
                    tema_categoria=canal_teste['tema_categoria'], tema_escolhido=tema_teste,
                    dupla_nomes=dupla_teste_nomes, roteiro_base_pt=roteiro_base_pt, idioma='pt'
                )
                if caminho_video: videos_gerados.append(caminho_video)
        else:
            print("Fim do teste: Nenhum tema novo para processar.")
        print("\n--- MODO DE TESTE DE DIÁLOGO CONCLUÍDO ---")
    else:
        print("--- INICIANDO CICLO DE PRODUÇÃO COMPLETO (9 VÍDEOS) ---")
        for canal_info in CANAIS_CONFIG:
            print(f"\n>>> Processando categoria: {canal_info['tema_categoria']} <<<")
            tema_base = get_and_archive_next_theme(canal_info['arquivo_temas'])
            if tema_base is None: continue
            dupla_nomes = canal_info['dupla']
            personagem1 = PERSONAGENS[dupla_nomes[0]]
            personagem2 = PERSONAGENS[dupla_nomes[1]]
            roteiro_base_pt = generate_dialogue_script(tema_base, personagem1, personagem2, canal_info['objetivo'])
            if roteiro_base_pt:
                for idioma in ['pt', 'en', 'es']:
                    caminho_video = create_video(
                        tema_categoria=canal_info['tema_categoria'], tema_escolhido=tema_base,
                        dupla_nomes=dupla_nomes, roteiro_base_pt=roteiro_base_pt, idioma=idioma
                    )
                    if caminho_video: videos_gerados.append(caminho_video)
        print("\n🎉 Ciclo de produção concluído!")
    return videos_gerados

if __name__ == '__main__':
    main(modo_teste=True)