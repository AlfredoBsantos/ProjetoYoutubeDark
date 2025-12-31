import os
import sys
import time
import random
import re
import shutil
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import ollama

# --- CONFIGURAÇÕES ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_VIDEOS_GERADOS = os.path.join(BASE_DIR, "output", "videos_gerados")
PASTA_VIDEOS_POSTADOS = os.path.join(BASE_DIR, "output", "videos_postados")
os.makedirs(PASTA_VIDEOS_POSTADOS, exist_ok=True)
HORARIOS_POSTAGEM = ["07:00", "12:00", "16:00", "19:00", "21:00"]

def limpar_para_selenium(texto):
    """Remove caracteres não-BMP (como a maioria dos emojis) de uma string."""
    return ''.join(c for c in texto if c <= '\uFFFF')

def gerar_metadados_com_ia(tema_video, idioma, personagem1, personagem2):
    """Gera Título, Descrição e Tags para o vídeo usando a IA local."""
    print(f"\nGerando metadados com IA para o tema: {tema_video}")
    lang_map = {'pt': 'Português', 'en': 'Inglês', 'es': 'Espanhol'}
    prompt = f"""
    Sua tarefa é agir como um especialista em SEO para YouTube Shorts. Crie um Título, uma Descrição curta e Hashtags para um vídeo.
    ### CONTEXTO DO VÍDEO
    - Tema: "{tema_video}"
    - Personagens: {personagem1} e {personagem2}
    - Idioma: {lang_map.get(idioma, 'Português')}
    - Formato: Diálogo curto e filosófico/divertido para YouTube Shorts.
    ### REGRAS
    - Título: Deve ser curto, chamativo, em formato de pergunta ou polêmico (máximo 70 caracteres). NÃO use emojis.
    - Descrição: Uma frase que complemente o título. Inclua a frase "Este diálogo foi 100% gerado por Inteligência Artificial."
    - Hashtags: Uma lista de 5 a 10 hashtags relevantes, separadas por vírgula e sem o #.
    ### ESTRUTURA DA SAÍDA (use este formato EXATO)
    TITULO: [Seu título aqui]
    DESCRICAO: [Sua descrição aqui]
    HASHTAGS: [sua, lista, de, hashtags, aqui]
    """
    try:
        response = ollama.chat(model='gemma3', messages=[{'role': 'user', 'content': prompt}])
        content = response['message']['content']
        titulo = re.search(r"TITULO: (.*)", content).group(1)
        descricao = re.search(r"DESCRICAO: (.*)", content).group(1)
        hashtags_str = re.search(r"HASHTAGS: (.*)", content).group(1)
        hashtags = [tag.strip() for tag in hashtags_str.split(',')]
        titulo_limpo = limpar_para_selenium(titulo)
        descricao_limpa = limpar_para_selenium(descricao)
        return {"titulo": titulo_limpo, "descricao": descricao_limpa, "tags": hashtags}
    except Exception as e:
        print(f"❌ Erro ao gerar metadados com IA: {e}")
        return None

def main():
    print("--- INICIANDO ROBÔ DE UPLOAD ---")
    
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 60)
    except Exception as e:
        print(f"❌ Erro ao conectar ao Chrome. Verifique se você o iniciou com o modo de depuração.")
        return

    videos_para_upar = [f for f in os.listdir(PASTA_VIDEOS_GERADOS) if f.endswith(".mp4")]
    if not videos_para_upar:
        print("Nenhum vídeo novo encontrado na pasta de geração. Encerrando.")
        if driver: driver.quit()
        return

    for video_nome in videos_para_upar:
        try:
            caminho_completo_video = os.path.join(PASTA_VIDEOS_GERADOS, video_nome)
            partes_nome = video_nome.replace('.mp4', '').split('_')
            categoria, idioma, tema_curto = partes_nome[0], partes_nome[1].lower(), "_".join(partes_nome[2:])
            dupla_nomes = next((c['dupla'] for c in config.CANAIS_CONFIG if c['tema_categoria'] == categoria), None)
            if not dupla_nomes: continue
            
            metadados = gerar_metadados_com_ia(tema_curto.replace('_', ' '), idioma, dupla_nomes[0], dupla_nomes[1])
            if not metadados:
                print(f"Não foi possível gerar metadados para {video_nome}. Pulando.")
                continue

            print(f"\nFazendo upload de: {video_nome}")
            
            driver.get("https://studio.youtube.com")
            
            # 1. Inicia o Upload
            wait.until(EC.element_to_be_clickable((By.ID, "create-button"))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//ytcp-text-menu//yt-formatted-string[contains(text(), 'Enviar vídeos')]"))).click()
            upload_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            upload_input.send_keys(caminho_completo_video)
            
            # 2. Preenche Título e Descrição
            print("Preenchendo detalhes...")
            titulo_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//ytcp-mention-textbox[@id='title-textarea']//div[@id='textbox']")))
            titulo_input.click(); time.sleep(0.5); titulo_input.send_keys(Keys.CONTROL + "a"); time.sleep(0.5); titulo_input.send_keys(Keys.DELETE); time.sleep(0.5)
            titulo_input.send_keys(metadados['titulo'])
            
            desc_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//ytcp-mention-textbox[@id='description-textarea']//div[@id='textbox']")))
            desc_input.click(); time.sleep(0.5); desc_input.send_keys(Keys.CONTROL + "a"); time.sleep(0.5); desc_input.send_keys(Keys.DELETE); time.sleep(0.5)
            desc_input.send_keys(metadados['descricao'])

            # 3. Seleciona "Não é conteúdo para crianças"
            not_for_kids_radio = wait.until(EC.element_to_be_clickable((By.NAME, "NOT_MADE_FOR_KIDS")))
            driver.execute_script("arguments[0].click();", not_for_kids_radio)
            
            # 4. Avança pelas telas
            for i in range(3):
                next_button = wait.until(EC.element_to_be_clickable((By.ID, "next-button")))
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)

            # 5. Agenda o vídeo
            print("Agendando o vídeo...")
            schedule_button = wait.until(EC.element_to_be_clickable((By.ID, "schedule-radio-button")))
            driver.execute_script("arguments[0].click();", schedule_button)
            
            # 6. Clica no botão final "Programar"
            done_button = wait.until(EC.element_to_be_clickable((By.ID, "done-button")))
            driver.execute_script("arguments[0].click();", done_button)
            
            print(f"✅ Vídeo '{metadados['titulo']}' agendado com sucesso!")
            wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), 'Vídeo programado')]")))
            time.sleep(5)

            # 7. Move o arquivo para a pasta de postados
            shutil.move(caminho_completo_video, os.path.join(PASTA_VIDEOS_POSTADOS, video_nome))
            
        except Exception:
            print(f"❌ Ocorreu um erro inesperado ao tentar fazer o upload de {video_nome}:")
            traceback.print_exc()
            continue

    print("\n--- CICLO DE UPLOADS CONCLUÍDO ---")
    if driver: driver.quit()

if __name__ == '__main__':
    main()