# Mike — guia de instalação para Windows

Este guia explica como preparar o Mike pela primeira vez, mesmo que você
tenha pouca experiência com programação. Siga as etapas na ordem.

## O que o Mike precisa

- Windows 11 de 64 bits.
- Python 3.15 de 64 bits. É a versão testada neste projeto e tem os pacotes
  de áudio necessários disponíveis.
- Visual Studio Code (VS Code).
- Ollama instalado e o modelo `qwen3:4b` baixado.
- Microfone para conversar por voz. Fones de ouvido são recomendados para
  evitar que o microfone capte a resposta do Mike.
- Internet durante a instalação e na primeira inicialização do reconhecimento
  de voz.

O reconhecimento de voz é executado localmente com Whisper. O áudio falado
não é enviado para uma API de transcrição. Na primeira inicialização, o Mike
baixa o modelo Whisper `small` (aproximadamente 465 MB); depois, esse arquivo
fica armazenado no computador. As respostas são geradas pelo Ollama local.

## 1. Instale o Python

1. Baixe e instale Python 3.15 de 64 bits pelo site oficial:
   [python.org/downloads](https://www.python.org/downloads/).
2. Durante a instalação, habilite **Add python.exe to PATH**, se essa opção
   aparecer. O instalador também pode oferecer o Python Launcher.
3. Quando a instalação terminar, feche e reabra o VS Code se ele já estiver
   aberto.
4. No VS Code, abra **Terminal > Novo Terminal** e execute:

   ```powershell
   py -3.15 --version
   ```

   O resultado deve começar com `Python 3.15`. Se o comando `py` não existir,
   feche e reabra o VS Code; se continuar sem funcionar, instale novamente o
   Python pelo site oficial, incluindo o Python Launcher.

## 2. Abra a pasta do projeto no VS Code

1. No VS Code, escolha **Arquivo > Abrir Pasta...**.
2. Selecione a pasta que contém `app.py` e `requirements.txt`.
3. Abra o terminal integrado com **Terminal > Novo Terminal**. Os comandos
   abaixo devem ser executados dentro dessa pasta.

Para conferir se está na pasta correta, execute:

```powershell
Get-ChildItem
```

Na lista devem aparecer `app.py` e `requirements.txt`.

## 3. Crie o ambiente Python e instale as dependências

O ambiente virtual (`.venv`) mantém as bibliotecas do Mike separadas de outros
programas do computador. No terminal do VS Code, execute:

```powershell
py -3.15 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

A instalação inclui o Whisper local, acesso ao microfone e a síntese de voz
do Windows. Ela pode levar alguns minutos. Não feche o terminal enquanto o
comando estiver instalando os pacotes.

Confirme que a instalação terminou:

```powershell
.\.venv\Scripts\python.exe -m pip check
```

Se aparecer `No broken requirements found`, as dependências estão instaladas.

> **Se `.venv` já existir:** não crie nem apague outro ambiente às cegas.
> Confira primeiro a versão com
> `.\.venv\Scripts\python.exe --version`. Para este projeto, use Python 3.15.
> Se o ambiente tiver outra versão, peça ajuda antes de substituí-lo, pois
> apagar uma pasta `.venv` é uma ação permanente.

## 4. Instale e prepare o Ollama

1. Instale o Ollama pelo site oficial:
   [ollama.com/download](https://ollama.com/download).
2. Abra um terminal do VS Code e confirme que ele está disponível:

   ```powershell
   ollama --version
   ```

3. Baixe o modelo usado pelo Mike:

   ```powershell
   ollama pull qwen3:4b
   ```

   O modelo ocupa aproximadamente 2,5 GB. Esse download é necessário apenas
   uma vez neste computador.
4. Confirme que o modelo aparece na lista:

   ```powershell
   ollama list
   ```

   A lista deve incluir `qwen3:4b`.

O Ollama precisa estar em execução para o Mike responder. Normalmente, o
aplicativo do Ollama permanece ativo depois da instalação. Se o Mike disser
que não consegue se conectar, abra o Ollama pelo menu Iniciar e tente de novo.
Se necessário, inicie `ollama serve` em um terminal separado e deixe esse
terminal aberto enquanto usa o Mike.

## 5. Faça um primeiro teste em modo texto

Antes de configurar o microfone, teste a conversa com o Ollama:

```powershell
.\.venv\Scripts\python.exe app.py --texto
```

Quando aparecer `Você:`, escreva uma mensagem e pressione Enter. Para sair,
digite `sair`.

Se o Mike responder, Python, as dependências, o Ollama e o modelo estão
conectados. O modo texto é opcional; sem `--texto`, o programa inicia em modo
de voz.

## 6. Inicie a conversa por voz

Na pasta do projeto, execute:

```powershell
.\.venv\Scripts\python.exe app.py
```

Na primeira execução, o Mike baixa o modelo Whisper `small` (aproximadamente
465 MB). É necessário ter internet durante esse download. Aguarde as mensagens
de carregamento terminarem. Nas execuções seguintes, o modelo será reutilizado
localmente.

Quando aparecer `Mike iniciado. Modo de voz ativo` e
`Mike: Pode falar. Estou ouvindo.`, diga uma frase em português perto do
microfone. O Mike deve mostrar o texto reconhecido, consultar o modelo local,
exibir a resposta e reproduzi-la em voz alta. Ele só começa a ouvir o próximo
turno depois que termina de falar.

- Para encerrar, pressione **Ctrl+C** ou diga **“sair”**, **“encerrar”** ou
  **“parar”**.
- Para usar apenas texto, acrescente `--texto` ao comando.
- Para ajustar a velocidade da voz, use `--velocidade` com um valor entre
  80 e 300. Exemplo:

  ```powershell
  .\.venv\Scripts\python.exe app.py --velocidade 160
  ```

## 7. Crie um atalho na área de trabalho

Depois de concluir a instalação das dependências e do Ollama, você pode abrir
o Mike sem digitar comandos:

1. No Explorador de Arquivos, abra a pasta do projeto extraída do ZIP.
2. Localize `start-mike.bat`.
3. Clique com o botão direito nele e escolha **Mostrar mais opções >
   Enviar para > Área de trabalho (criar atalho)**. Em algumas versões do
   Windows, **Enviar para** aparece diretamente no menu.
4. Na área de trabalho, abra o atalho **start-mike**. O terminal vai iniciar
   o Mike em modo de voz. Para encerrar, pressione **Ctrl+C** ou diga **“sair”**.
5. Para iniciar em modo texto pelo atalho, abra as propriedades do atalho,
   acrescente `--texto` ao final do campo **Destino** e confirme. O inicializador
   repassa esse argumento ao Mike.

O inicializador procura o `.venv` e o `app.py` na própria pasta onde está
instalado. Por isso, ele funciona mesmo que o ZIP seja extraído em outra pasta
ou que o nome da conta do Windows seja diferente. Não copie o atalho da área
de trabalho do computador de outra pessoa: aquele atalho contém o caminho
particular daquela instalação. Cada pessoa deve criar o próprio atalho depois
de extrair e instalar o projeto.

Ao preparar o ZIP para compartilhar, inclua `app.py`, `requirements.txt`,
`README.md` e `start-mike.bat`. Não inclua a pasta `.venv`: seu amigo vai
criá-la no próprio computador seguindo este guia. Também não inclua
`mensagens.db` se ele contiver seu histórico pessoal; o Mike criará um banco
novo para ele na primeira execução.

Se o inicializador disser que o ambiente Python não foi encontrado, abra a
pasta do projeto no VS Code e conclua a etapa 3 deste guia. O atalho não instala
dependências automaticamente.

## 8. Microfone e voz do Windows

Se o Windows não permitir que o Mike use o microfone:

1. Abra **Configurações > Privacidade e segurança > Microfone**.
2. Habilite o acesso ao microfone e a permissão para aplicativos da área de
   trabalho.
3. Abra **Configurações > Sistema > Som > Entrada**, escolha o microfone
   correto e fale para confirmar que o indicador de entrada reage.
4. Feche e abra o Mike novamente.

O Mike procura uma voz de português do Brasil instalada no Windows. Se não
encontrar uma, ele avisa e continua respondendo em texto. Para verificar ou
adicionar uma voz, procure por **Configurações > Hora e idioma > Fala** e
instale uma voz de português (Brasil), se estiver disponível na sua edição do
Windows. A lista e os nomes das opções podem variar conforme a versão do
Windows.

## 9. Histórico e memória

O histórico fica no arquivo `mensagens.db`, na mesma pasta de `app.py`. O
programa cria esse banco automaticamente na primeira execução. As conversas
concluídas são armazenadas e as 12 mensagens mais recentes são carregadas para
o contexto quando o Mike inicia, tanto no modo de voz quanto no modo texto.
Os dois modos usam o mesmo histórico.

Não apague, renomeie nem compartilhe `mensagens.db` se quiser manter a memória
local. Para fazer uma cópia de segurança, feche o Mike e copie esse arquivo
para um local seguro. O arquivo chamado `mensages.db` (sem o segundo “n”)
não é o banco utilizado pelo programa.

## Solução de problemas

### `py` não é reconhecido

Feche e reabra o VS Code. Se continuar, reinstale Python 3.15 de 64 bits pelo
site oficial e habilite o Python Launcher. Confira com `py -3.15 --version`.

### Falha ao instalar uma dependência ou mensagem sobre versão incompatível

Confira se está usando Python 3.15 e instale pelo Python do ambiente do
projeto:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Não use um `pip` de outro Python.

### O Mike não consegue se conectar ao Ollama

Abra o aplicativo Ollama pelo menu Iniciar e confira se o modelo está instalado:

```powershell
ollama list
```

Se `qwen3:4b` não aparecer, execute `ollama pull qwen3:4b`. Depois, tente o
modo texto para confirmar a conexão.

### O Mike diz que não detectou fala

Essa mensagem significa que não foi detectada fala dentro do tempo de espera;
ele tenta ouvir novamente. Fale depois de aparecer **“Estou ouvindo...”**,
aproxime-se do microfone e confira o nível de entrada em **Configurações >
Sistema > Som > Entrada**. Se estiver usando um fone Bluetooth ou outro
dispositivo, selecione-o como entrada padrão do Windows.

### O microfone não está disponível ou ocorre erro de áudio

Confira a permissão de microfone do Windows, selecione o dispositivo correto
nas configurações de Som e reinicie o programa. Se o erro continuar, anote a
mensagem exibida no terminal e peça ajuda.

### Não há resposta falada

O Mike precisa de uma voz pt-BR instalada no Windows. Se a voz não estiver
disponível ou ocorrer um erro de reprodução, a resposta ainda deve aparecer
como texto no terminal.

### O primeiro início demora

O primeiro uso pode demorar porque o Whisper `small` precisa ser baixado e
carregado. Mantenha a internet ativa durante o download e aguarde a mensagem
**“Mike iniciado. Modo de voz ativo”**.
