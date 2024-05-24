# vox

Este é um script Python que permite a interação com os modelos GPT-3.5 e 4o. O script aceita argumentos de linha de comando e também permite a interação através de um prompt de entrada.

1. Configure o comportamento do programa no arquivo `configs.json`:

- `system`: configura o contexto da aplicação;
- `models`: lista os modelos;
- `aliases`: configura atalhos para comandos.

2. Edite a _variável de ambiente_ "OPENAI_API_KEY" no .env seguindo template. Não esqueça de remover o "-TEMPLATE".

## Uso

Com o _ambiente virtual_ ativo, instale as dependências usando `pip install -r requirements.txt`.

As únicas dependências são:

- `openai` (e ela tem suas próprias dependências) e
- `pyperclip` (para o caso de mexer com a área de transferência).

O script usa a api do GPT-4o por default, mas você pode iniciar a conversa com o 3.5 usando `python3 vox 3` e a conversa dura até um input "" ou ":q".

Você também pode especificar um argumento `-p` seguido de uma string com aspas para obter uma resposta rápida do modelo escolhido. Exemplo: `python3 vox 4 -p "Qual o seu nome?"`.

Se nenhum argumento de linha de comando for fornecido, o script entrará em um loop de entrada onde você pode digitar comandos:

- `:3`: Muda para o modelo GPT-3
- `:4`: Muda para o modelo GPT-4
- `:model`: Imprime na tela o modelo em uso
- `:c`: Copia a última mensagem do assistente para a área de transferência
- `:ca`: Concatena todas as mensagens mantendo as identificações e copia para a área de transferência.

Para sair do loop de entrada, basta pressionar Enter sem digitar nada ou digitar `:q`.

## Exemplo

Em `configs.json` podemos configurar os `aliases`. Um deles pode ser:

```json
"aliases": {
  ...
  "-kw": "extraia as palavras-chave",
  ...
}
```

e quando rodamos no terminal `python3 vox -p -kw -:p` o script:

- `python3 <path para o vox.py> -p` lê o que vem depois disso e considera como input;
- `-kw`: entende como "extraia as palavras-chave"...
- `-:p`: do conteúdo da área de transferência.
