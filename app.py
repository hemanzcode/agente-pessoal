import argparse
from contextlib import closing
from datetime import datetime
import json
import sqlite3
from pathlib import Path
import tempfile
import time
import urllib.request
import wave

URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:4b"
CAMINHO_BANCO = Path(__file__).resolve().parent / "mensagens.db"
LIMITE_HISTORICO = 12
FREQUENCIA_AUDIO = 16_000
DURACAO_BLOCO = 0.25
LIMITE_ESPERA_FALA = 15
DURACAO_MAXIMA_FALA = 30
LIMITE_SILENCIO = 1.2
LIMIAR_AUDIO = 0.012
MODELO_WHISPER = "small"

INSTRUCOES = """
Seu nome é Mike. Você é o agente pessoal do usuário.
Responda em português brasileiro, de forma natural,
clara e objetiva.
Considere o histórico da conversa antes de responder.
Não invente informações sobre o usuário.
"""


def inicializar_banco():
    with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao, conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )


def carregar_historico(limite=LIMITE_HISTORICO):
    with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao, conexao:
        registros = conexao.execute(
            """
            SELECT usuario, mensagem
            FROM historico
            ORDER BY id DESC
            LIMIT ?
            """,
            (limite,)
        ).fetchall()

    registros.reverse()
    return [
        {"role": usuario, "content": mensagem}
        for usuario, mensagem in registros
    ]


def salvar_historico(mensagens):
    timestamp = datetime.now().isoformat(timespec="seconds")
    registros = [
        (mensagem["role"], mensagem["content"], timestamp)
        for mensagem in mensagens
    ]

    with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao, conexao:
        conexao.executemany(
            """
            INSERT INTO historico (usuario, mensagem, timestamp)
            VALUES (?, ?, ?)
            """,
            registros
        )


def consultar_modelo(mensagens):
    dados = {
        "model": MODEL,
        "messages": mensagens,
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }

    requisicao = urllib.request.Request(
        URL,
        data=json.dumps(dados, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(requisicao, timeout=180) as resposta:
        resultado = json.loads(
            resposta.read().decode("utf-8")
        )

    resposta_mike = resultado["message"]["content"]
    return resposta_mike


inicializar_banco()
historico = carregar_historico()


def conversar(mensagem):
    mensagens = [
        {"role": "system", "content": INSTRUCOES},
        *historico[-LIMITE_HISTORICO:],
        {"role": "user", "content": mensagem}
    ]

    resposta_mike = consultar_modelo(mensagens)

    novas_mensagens = [
        {"role": "user", "content": mensagem},
        {"role": "assistant", "content": resposta_mike}
    ]
    salvar_historico(novas_mensagens)

    historico.extend(novas_mensagens)
    del historico[:-LIMITE_HISTORICO]

    return resposta_mike


def criar_sintetizador(velocidade):
    import pyttsx3

    sintetizador = pyttsx3.init()
    vozes = sintetizador.getProperty("voices")
    voz_portugues = next(
        (
            voz for voz in vozes
            if any(
                "pt-br" in (
                    idioma.decode("utf-8", errors="ignore")
                    if isinstance(idioma, bytes)
                    else str(idioma)
                ).lower()
                for idioma in voz.languages
            )
        ),
        None
    )

    if voz_portugues is None:
        print(
            "Aviso: não encontrei uma voz pt-BR instalada. "
            "O Mike continuará respondendo em texto."
        )
        encerrar_sintetizador(sintetizador)
        return None

    sintetizador.setProperty("voice", voz_portugues.id)
    sintetizador.setProperty("rate", velocidade)
    return sintetizador


def encerrar_sintetizador(sintetizador):
    if sintetizador is None:
        return

    try:
        sintetizador.stop()
    except Exception as erro:
        print(f"Erro ao encerrar o sintetizador de voz: {erro}")


def falar_resposta(sintetizador, texto):
    if sintetizador is None:
        return

    try:
        sintetizador.say(texto)
        sintetizador.runAndWait()
    except Exception as erro:
        print(f"Erro ao reproduzir a resposta em áudio: {erro}")


def capturar_audio():
    import numpy as np
    import sounddevice as sd

    bloco = int(FREQUENCIA_AUDIO * DURACAO_BLOCO)
    amostras = []
    inicio = time.monotonic()
    inicio_fala = None
    amostras_silencio = 0
    limite_amostras_silencio = int(FREQUENCIA_AUDIO * LIMITE_SILENCIO)

    with sd.InputStream(
        samplerate=FREQUENCIA_AUDIO,
        channels=1,
        dtype="float32",
        blocksize=bloco
    ) as microfone:
        while True:
            agora = time.monotonic()
            if inicio_fala is None and agora - inicio >= LIMITE_ESPERA_FALA:
                break
            if (
                inicio_fala is not None
                and agora - inicio_fala >= DURACAO_MAXIMA_FALA
            ):
                break

            audio, estado = microfone.read(bloco)
            if estado:
                print(f"Aviso do microfone: {estado}")

            audio = audio[:, 0].copy()
            nivel = float(np.sqrt(np.mean(np.square(audio, dtype=np.float64))))

            if inicio_fala is None:
                if nivel < LIMIAR_AUDIO:
                    continue
                inicio_fala = time.monotonic()
                print("Estou ouvindo...")

            amostras.append(audio)

            if nivel < LIMIAR_AUDIO:
                amostras_silencio += len(audio)
                if amostras_silencio >= limite_amostras_silencio:
                    break
            else:
                amostras_silencio = 0

    if not amostras:
        return None

    return np.concatenate(amostras)


def transcrever_audio(modelo_voz, audio):
    import numpy as np

    audio_pcm = np.clip(audio * 32767, -32768, 32767).astype("<i2")
    caminho_temporario = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as arquivo:
            caminho_temporario = Path(arquivo.name)

        with wave.open(str(caminho_temporario), "wb") as arquivo:
            arquivo.setnchannels(1)
            arquivo.setsampwidth(2)
            arquivo.setframerate(FREQUENCIA_AUDIO)
            arquivo.writeframes(audio_pcm.tobytes())

        segmentos = modelo_voz.transcribe(
            str(caminho_temporario),
            language="pt"
        )
        return " ".join(segmento.text.strip() for segmento in segmentos).strip()
    finally:
        if caminho_temporario is not None:
            caminho_temporario.unlink(missing_ok=True)


def iniciar_conversa_por_voz(velocidade):
    import sounddevice as sd
    from pywhispercpp.model import Model

    try:
        dispositivo = sd.query_devices(kind="input")
    except sd.PortAudioError as erro:
        print(
            "Não encontrei um microfone disponível. Conecte ou habilite "
            f"um microfone e tente novamente. Detalhes: {erro}"
        )
        return

    print(f"Microfone: {dispositivo['name']}")
    sintetizador = None

    try:
        sintetizador = criar_sintetizador(velocidade)
    except Exception as erro:
        print(f"Erro ao preparar a voz do Mike; seguirei em texto: {erro}")

    print(
        f"Carregando o reconhecimento local ({MODELO_WHISPER}). "
        "Na primeira execução, o modelo será baixado para esta máquina."
    )
    try:
        modelo_voz = Model(
            MODELO_WHISPER,
            n_threads=4,
            print_realtime=False,
            print_progress=False
        )
    except Exception as erro:
        print(f"Não foi possível preparar o reconhecimento de voz local: {erro}")
        print("Verifique a conexão para o primeiro download do modelo e tente novamente.")
        encerrar_sintetizador(sintetizador)
        return

    print("Mike iniciado. Modo de voz ativo. Pressione Ctrl+C para sair.")

    try:
        while True:
            print("\nMike: Pode falar. Estou ouvindo.")
            try:
                audio = capturar_audio()
            except sd.PortAudioError as erro:
                print(f"Erro ao acessar o microfone: {erro}")
                break

            if audio is None:
                print("Não detectei fala. Vou tentar ouvir novamente.")
                continue

            try:
                mensagem = transcrever_audio(modelo_voz, audio)
            except Exception as erro:
                print(f"Erro ao transcrever o áudio localmente: {erro}")
                continue

            if len(mensagem) < 2:
                print("Não consegui reconhecer uma mensagem. Pode repetir.")
                continue

            print(f"\nVocê: {mensagem}")
            if mensagem.casefold() in {"sair", "encerrar", "parar"}:
                print("Até mais!")
                break

            try:
                resposta = conversar(mensagem)
            except Exception as erro:
                print(f"Erro ao conversar ou salvar o histórico: {erro}")
                continue

            print(f"\nMike: {resposta}")
            falar_resposta(sintetizador, resposta)
    except KeyboardInterrupt:
        print("\nMike encerrado.")
    finally:
        encerrar_sintetizador(sintetizador)


def iniciar_conversa_por_texto():
    print("Mike iniciado. Digite 'sair' para encerrar.")

    while True:
        try:
            mensagem = input("\nVocê: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nMike encerrado.")
            break

        if mensagem.lower() == "sair":
            print("Até mais!")
            break

        if not mensagem:
            continue

        try:
            print("\nMike:", conversar(mensagem))
        except Exception as erro:
            print(f"\nErro ao conversar ou salvar o histórico: {erro}")


def main():
    parser = argparse.ArgumentParser(description="Agente pessoal Mike")
    parser.add_argument(
        "--texto",
        action="store_true",
        help="inicia no modo de conversa por texto"
    )
    parser.add_argument(
        "--velocidade",
        type=int,
        default=200,
        help="velocidade da voz do Mike (padrão: 200)"
    )
    argumentos = parser.parse_args()

    if not 80 <= argumentos.velocidade <= 300:
        parser.error("a velocidade deve estar entre 80 e 300")

    if argumentos.texto:
        iniciar_conversa_por_texto()
    else:
        iniciar_conversa_por_voz(argumentos.velocidade)


if __name__ == "__main__":
    main()
