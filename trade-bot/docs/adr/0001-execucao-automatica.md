# ADR 0001: Execução automática com travas no código

- Status: Aceita · Data: 2026-10-28

## Contexto

O projeto de referência (`day-trader-skill`) exige um "sim" humano por ordem e
nunca fala com a corretora diretamente. O dono pediu execução **automática com
dinheiro real**.

## Decisão

- O robô chama a API REST da Alpaca diretamente, sem confirmação por ordem.
- A confirmação humana passa a ser **uma vez por sessão de execução**: modo `live` no config, mais uma frase em variável de ambiente, mais chaves live separadas (SEC-02).
- Os limites ficam no código e na corretora, não no "bom senso" do modelo:
  - ordens bracket (stop na corretora);
  - limites diários;
  - tetos de 5% e 2% do patrimônio no modo live;
  - kill switch;
  - zerar tudo às 15:55.
- O Claude (LLM) **não** decide as operações. As regras são determinísticas e testadas, e o Claude serve para desenvolver e revisar.

## Consequências

- Mais rápido e sem depender de alguém online, mas um bug pode gerar perdas. Por isso o harness e os critérios de aceite da SPEC §6 são obrigatórios antes do modo live.
- Implementação própria em Python puro (sem copiar código do projeto de referência) para controlar 100% do que roda.
