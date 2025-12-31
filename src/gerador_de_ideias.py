# src/gerador_de_ideias.py (Versão Final Híbrida: Reddit + IA Local)

import os
import random
import re
import sys
import praw   # Para o Reddit
import ollama # Para a IA Local

# Adiciona o diretório raiz ao path para que possamos importar o config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# --- 1. CONFIGURAÇÃO INICIAL (LENDO DO ARQUIVO CONFIG) ---
# Autenticação com o Reddit
reddit = praw.Reddit(
    client_id=config.REDDIT_CLIENT_ID,
    client_secret=config.REDDIT_CLIENT_SECRET,
    user_agent=config.REDDIT_USER_AGENT,
    username=config.REDDIT_USERNAME,
    password=config.REDDIT_PASSWORD,
)
CANAIS_CONFIG = config.CANAIS_CONFIG

# --- CONFIGURAÇÃO DE PASTAS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_TEMAS = os.path.join(BASE_DIR, "assets", "themes")

# --- ESTRATÉGIA: SUBREDDITS-SEMENTE PARA CADA CATEGORIA ---
MAPA_DE_SUBREDDITS = {
    "Filosofia": ["brasil", "filosofia", "PergunteReddit"],
    "Desenvolvimento Pessoal": ["desabafos", "investimentos", "conselhos"],
    "Curiosidades": ["futurology", "ciencia", "noticias", "HojeEuAprendi"]
}


# --- 2. FUNÇÕES AUXILIARES ---

def buscar_topicos_no_reddit(subreddit_name):
    """Busca os posts mais 'quentes' de um subreddit."""
    print(f"\nBuscando tópicos quentes no r/{subreddit_name}...")
    try:
        subreddit = reddit.subreddit(subreddit_name)
        top_posts = subreddit.hot(limit=10)
        titulos = [post.title for post in top_posts]
        print(f"Tópicos encontrados: {titulos[:3]}...")
        return titulos
    except Exception as e:
        print(f"❌ Erro ao buscar tópicos no r/{subreddit_name}: {e}")
        return []

def criar_tema_com_ia_local(titulo_post, categoria, objetivo_canal):
    """Usa o Ollama com o modelo local para transformar um título do Reddit em uma ideia de vídeo."""
    print(f"\nUsando IA local para transformar o post: '{titulo_post[:50]}...'")
    
    prompt = f"""
    Sua única tarefa é transformar o 'Título de Post do Reddit' abaixo em uma única pergunta intrigante para um vídeo de um canal sobre '{categoria}' com o objetivo de '{objetivo_canal}'.

    REGRAS ESTRITAS:
    1. A saída DEVE SER apenas a pergunta.
    2. NÃO forneça opções, listas, explicações ou qualquer texto extra.
    3. A pergunta deve ser curta, polêmica e viral.

    ---
    TAREFA:
    - Título de Post do Reddit: "{titulo_post}"
    - Categoria: "{categoria}"
    - Pergunta para Vídeo:
    """
    
    try:
        response = ollama.chat(
            model='gemma3', # Usando o modelo que você baixou
            messages=[{'role': 'user', 'content': prompt}]
        )
        ideia = response['message']['content'].strip().split('\n')[0].replace('*', '').replace('"', '')
        print(f"Ideia final gerada: {ideia}")
        return ideia
    except Exception as e:
        print(f"❌ Erro ao se comunicar com o Ollama: {e}")
        print("   Verifique se o aplicativo Ollama está rodando no seu computador.")
        return None

def salvar_ideia(ideia, arquivo_tema_nome):
    """Salva a nova ideia no arquivo de temas correspondente."""
    caminho_arquivo = os.path.join(PASTA_TEMAS, arquivo_tema_nome)
    try:
        with open(caminho_arquivo, 'a', encoding='utf-8') as f:
            f.write(f'\n{ideia}')
        print(f"✅ Ideia salva com sucesso em {caminho_arquivo}")
    except Exception as e:
        print(f"❌ Erro ao salvar ideia em {caminho_arquivo}: {e}")

# --- 3. FUNÇÃO PRINCIPAL ---
def main():
    """Função principal que executa a geração de ideias."""
    print("--- INICIANDO GERAÇÃO DE IDEIAS HÍBRIDA (REDDIT + IA LOCAL) ---")
    
    for canal_info in CANAIS_CONFIG:
        categoria = canal_info['tema_categoria']
        arquivo_tema = canal_info['arquivo_temas']
        objetivo = canal_info['objetivo']
        
        subreddits_da_categoria = MAPA_DE_SUBREDDITS[categoria]
        subreddit_aleatorio = random.choice(subreddits_da_categoria)
        
        topicos_encontrados = buscar_topicos_no_reddit(subreddit_aleatorio)
        
        if topicos_encontrados:
            topico_do_momento = random.choice(topicos_encontrados)
            ideia_final = criar_tema_com_ia_local(topico_do_momento, categoria, objetivo)
            
            if ideia_final and '?' in ideia_final and len(ideia_final) > 10:
                salvar_ideia(ideia_final, arquivo_tema)
            else:
                print(f"Ideia final ('{ideia_final}') não parece válida, descartando.")
        else:
            print(f"Nenhuma ideia encontrada para a categoria '{categoria}' no r/{subreddit_aleatorio}.")
            
    print("\n--- Geração de ideias concluída! ---")

if __name__ == '__main__':
    main()