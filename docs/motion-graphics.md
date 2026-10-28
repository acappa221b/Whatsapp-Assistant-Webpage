# Motion graphics com o Claude

O Claude não "gera vídeo" diretamente. Ele **escreve uma página HTML animada**
(CSS/GSAP/Canvas), e uma ferramenta grava essa página quadro a quadro em MP4.
É isso que aparece nos vídeos "o Claude agora faz motion graphics".

## Caminho recomendado: HyperFrames (já incluso)

Requisitos: Node.js ≥ 22 e FFmpeg instalados no seu computador.

```bash
./scripts/install-skills.sh            # instala as skills de vídeo (pack "video")
npx hyperframes init meu-video
cd meu-video && npx hyperframes preview   # abre o preview no navegador
npx hyperframes render                    # gera o MP4
```

No Claude Code, peça por exemplo:

> Use a skill hyperframes. Crie um vídeo de lançamento de 15 s, 1080×1920,
> para o produto X: logo entrando, 3 benefícios com texto cinético e CTA final.
> Siga o DESIGN.md do projeto para cores e fontes.

Combine com `./scripts/use-design.sh <marca> meu-video` para herdar uma paleta pronta.

## Vídeo de lançamento do seu projeto: `/brag`

Com o pack `brag` instalado, dentro da pasta de um projeto seu (site ou app), peça no Claude Code:

```
/brag --tone polished --format vertical
```

Ele lê o código, planeja o roteiro, monta a animação com o HyperFrames e
renderiza `brag.mp4` com trilha, efeitos e texto para postar. Ao publicar com a
trilha padrão, credite: "Music: Sascha Ende, ende.app (CC BY 4.0)".

## Galerias de prompts (só links: o conteúdo é dos criadores)

Não encontramos licença aberta para essas coleções, por isso os prompts **não
foram copiados** para este repositório. Use as galerias como inspiração.

| Galeria | O que tem | Observação |
| --- | --- | --- |
| https://prompt-motion.com | ~230 animações feitas com o Claude, cada uma com o prompt | Grátis; provável fonte do vídeo "centenas de animações" (não confirmado) |
| https://ai-x-leaders.com/en/prompt/ | ~26 vídeos com prompt | Sem cadastro |
| https://fliki.ai/features/claude-motion-graphics | ~83 vídeos | Página comercial |
| https://www.revid.ai/claude-motion-graphics | ~64 vídeos | Abrir o prompt no editor exige cadastro |

Cuidado com perfis que pedem "comente X que eu te mando o link" e depois
oferecem pacotes pagos: o conteúdo acima é gratuito.
