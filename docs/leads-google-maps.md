# Leads do Google Maps (Google Maps Scraper Kit)

Kit em `vendor/google-maps-scraper-kit/` (MIT, Mahanaicoach). Ele roda **no seu
computador** um extrator em Docker (`gosom/google-maps-scraper`) e uma skill que
deixa o Claude pedir buscas como "padarias em Pouso Alegre" e limpar a planilha.

## ⚠️ Leia antes de usar

- **Termos do Google:** raspar o Google Maps viola os Termos da Google Maps
  Platform (o próprio README do kit admite). Na prática o risco é ter o IP
  bloqueado. Uso comercial também traz risco jurídico.
- **LGPD:** telefone e e-mail de MEI, autônomo ou funcionário com nome são **dados
  pessoais**. Para prospectar, você precisa de:
  - base legal, em geral legítimo interesse (art. 7º, IX), com avaliação escrita;
  - informar de onde veio o dado e oferecer a saída (arts. 9º e 18);
  - guardar só o necessário (art. 6º).
  A multa da ANPD pode chegar a 2% do faturamento, limitada a R$ 50 milhões.
- **WhatsApp:** a política do WhatsApp Business exige opt-in antes de mandar
  mensagem. Disparo em massa para lista raspada leva a banimento do número.
- **Telemetria:** o motor envia estatísticas anônimas ao PostHog por padrão.
  Desligue com `DISABLE_TELEMETRY=1`, como mostrado abaixo.
- **Permissões:** o `.claude/settings.json` do kit libera o Claude para rodar
  `docker compose` e os scripts sem perguntar. Revise antes de abrir o projeto.

Isto não é aconselhamento jurídico.

## Como usar (no seu computador, com Docker instalado)

```bash
cp -r vendor/google-maps-scraper-kit ~/maps-leads && cd ~/maps-leads
echo "DISABLE_TELEMETRY=1" >> .env      # desliga a telemetria
# confira se o docker-compose.yml repassa o .env ao serviço; se não, adicione:
#   environment: [ "DISABLE_TELEMETRY=1" ]
claude                                   # abra o Claude Code na pasta e siga o SETUP.md
```

Uso mais seguro: buscar **empresas** (CNPJ, telefone comercial do Google) para
pesquisa de mercado, e não montar listas de pessoas para disparo.
