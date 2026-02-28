@CONTEXTO
Estou na raiz do projeto.
- Diretório de destino para scripts/outputs: `./my_masters_degree/taskmaster-analysis`
- Ambiente: Gerenciado por `uv` em `./.venv` (biblioteca `datasets` já instalada).
- Referência: O repo oficial está em `./notebooks/datasets/Taskmaster/TM-1-2019`, mas usaremos o HuggingFace para obter o conteúdo dos diálogos.
- Esta é a `Task2`, ler a `Task1` e seu respectivo `log` no mesmo repositório para obter maior contexto do que foi feito.

@TAREFA
Atue como um Cientista de Dados. Sua missão é criar um script Python para baixar, processar e gerar estatísticas do dataset "Taskmaster-1" (versão 2019).

1. PREPARAÇÃO DO SCRIPT


2. ANÁLISE ESTRUTURADA


3. GERAÇÃO DE ARTEFATOS


4. DEPENDÊNCIAS E EXECUÇÃO


@AÇÃO FINAL
Escreva o código, crie a pasta de resultados se não existir (via os/pathlib no python) e execute o script.

@CONFIGURAÇÃO
- Seja autônomo
- **Primeira ação:** Criar o arquivo `execution_plan_task2.md`.
- **Penúltima ação:** Criar um arquivo markdown com as tarefas adicionais, que não haviam sido planejadas, num arquivo `execution_log_task2_[datetime].md`. Adicione o `Summary` de execução no log também.
- **Última ação:** Confirmar que os arquivos PNG e TXT foram gerados com sucesso.