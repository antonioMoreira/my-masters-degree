@CONTEXTO
Estou na raiz do projeto.
- Diretório de destino para scripts/outputs: ./my_masters_degree/taskmaster-analysis
- Ambiente: Gerenciado por `uv` em ./.venv (biblioteca `datasets` já instalada).
- Referência: O repo oficial está em `./notebooks/datasets/Taskmaster/TM-1-2019`, mas usaremos o HuggingFace para obter o conteúdo dos diálogos.

@TAREFA
Atue como um Cientista de Dados. Sua missão é criar um script Python para baixar, processar e gerar estatísticas do dataset "Taskmaster-1" (versão 2019).

1. PREPARAÇÃO DO SCRIPT
   - Complemente o arquivo: `./my_masters_degree/taskmaster-analysis/eda_taskmaster_hf.py`.
   - O conteúdo do repositório do `HuggingFace` (`google-research-datasets/taskmaster1`) está em `./my_masters_degree/taskmaster-analysis/data`.
   - **Verificação de Metadados:** Verifique se o objeto json dos diálogos possui chaves de tempo (timestamps/duration). Se não houver, foque as métricas de tempo em "estimativas" ou deixe explícito no log, mas calcule as métricas de tokens e segmentos obrigatoriamente.

2. ANÁLISE ESTRUTURADA (Refinamento)
   Implemente cálculos para gerar uma tabela estatística (DataFrame) com as colunas [Max, Min, Average] para os seguintes critérios:
   - **Sample Duration (min):** Tempo total do diálogo (se houver timestamps).
   - **#Segments Per Sample:** Quantidade de turnos/utterances por diálogo.
   - **Segment Duration (s):** Tempo de cada turno individual (se houver timestamps).
   - **#Tokens Per Segment:** Quantidade de palavras/tokens por turno (use split por espaço simples ou `nltk` se disponível).
   - **#Segments Per Speaker:** Média de turnos agrupada por falante (User vs System).

3. GERAÇÃO DE ARTEFATOS
   Salve os seguintes arquivos em `./my_masters_degree/taskmaster-analysis/`:
   - `results/detailed_stats_table.csv`: A tabela com as métricas acima (Max, Min, Avg).
   - `results/detailed_stats_summary.txt`: Versão textual legível da tabela.
   - `data/sample_dialogues.json`: Salve uma amostra aleatória de 5 diálogos completos (com estrutura json preservada) para inspeção qualitativa. *Nota: Crie a pasta `data` se não existir.*

4. DEPENDÊNCIAS E EXECUÇÃO
   - Use `pandas` para estruturar a tabela de estatísticas.
   - Se precisar de tokenização simples, use métodos de string do Python para não inflar dependências, ou verifique se bibliotecas de NLP estão no ambiente.
   - Execute o script usando o `uv`: `uv run ./my_masters_degree/taskmaster-analysis/eda_taskmaster_hf.py`.

@AÇÃO FINAL
Escreva o código, crie a pasta de resultados se não existir (via os/pathlib no python) e execute o script.

@CONFIGURAÇÃO
- Seja autônomo
- **Primeira ação:** Criar o arquivo `execution_plan_task1.md`.
- **Penúltima ação:** Criar um arquivo markdown com as tarefas adicionais, que não haviam sido planejadas, num arquivo `execution_log_task1_[datetime].md`. Adicione o `Summary` de execução no log também.
- **Última ação:** Confirmar que os arquivos PNG e TXT foram gerados com sucesso.