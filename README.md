# ✂️ EYXO | KA Compressor

**Compressão inteligente de PNG com preservação de transparência**

---

## O que faz

- Comprime PNGs com alvo de peso exato (KB) definido por imagem
- Preserva alpha/transparência total (RGBA)
- Processa 100% local — nenhum arquivo sai do seu computador
- Empacota o resultado em `.zip` ou download avulso

## Como instalar

1. Baixe e extraia o ZIP do plugin
2. No Figma Desktop: `Plugins` → `Development` → `Import plugin from manifest...`
3. Selecione o arquivo `manifest.json` dentro da pasta extraída

## Como usar

1. Abra o plugin em qualquer página do Figma
2. Todos os frames da página aparecem listados automaticamente
3. Marque quais frames comprimir e defina o alvo de KB para cada um
4. Clique em **Comprimir** — o resultado aparece na tela em segundos
5. Baixe o pacote final (`.zip`) ou cada imagem individualmente

---

## Tecnologia

- **Motor de compressão:** Median-Cut + Floyd-Steinberg Dithering (algoritmo equivalente ao `pngquant`) — Canvas API nativa
- **Privacidade:** zero permissões de rede, zero upload, funciona offline

---

## Histórico (Changelog)

- **v5.0.2** - Correção crítica de qualidade: quantizador substituído por Median-Cut + Floyd-Steinberg dithering (preserva gradientes e sombras).
- **v5.0.1** - Correção: motor de compressão migrado de Web Worker para thread principal (compatibilidade com sandbox do Figma).
- **v5.0.0** - Migração completa para plugin Figma standalone: compressão 100% local, servidor Render removido, pasta reorganizada.

