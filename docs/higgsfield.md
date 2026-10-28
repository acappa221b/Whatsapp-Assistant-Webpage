# Claude + Higgsfield (imagens e vídeos de produto)

O vídeo que mostra isso é **publicidade paga** ("Parceria paga"). A integração
existe e é oficial, mas o serviço **é pago**: cada imagem ou vídeo consome
créditos. O plano grátis praticamente não tem créditos, e o teste de 3 dias pede
cartão e vira assinatura se não for cancelado. Os planos começam em cerca de
US$ 15-19/mês (confira no site, os valores mudam).

## Conectar

- **Claude (app/web):** Configurações → Conectores → Adicionar conector
  personalizado → `https://mcp.higgsfield.ai/mcp` → entrar com a conta Higgsfield.
- **Claude Code:** CLI oficial em https://github.com/higgsfield-ai/cli e skills
  em https://github.com/higgsfield-ai/skills (MIT).

Cuidado: algumas dessas skills mandam o Claude rodar
`curl ... install.sh | sh`, que baixa e executa um instalador sem revisão. Prefira
instalar a CLI você mesmo, lendo o script antes.

Alternativa gratuita já neste toolkit: `vendor/hyperframes` (vídeo a partir de
HTML) + `vendor/brag`.

Ajuda oficial: https://higgsfield.ai/creator-hub/help-center/mcp-cli/how-do-i-connect-higgsfield-to-claude
