# ✂️ EYXO | KA Compressor

**Compressão inteligente de PNG com preservação de transparência — direto no Figma, sem servidor.**

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

- **Motor de compressão:** `libimagequant-wasm` (mesma engine do `pngquant`) + fallback Canvas API
- **Execução:** Web Worker local — não trava a interface durante a compressão
- **Privacidade:** zero permissões de rede, zero upload, funciona offline

---

## Histórico (Changelog)

- **v5.0.0** - Migração completa para plugin Figma standalone: compressão 100% local via WASM, servidor Render removido, pasta reorganizada.
- **v4.10.0** - Plugin do Figma respeita as configurações de exportação nativas do nó (resolução customizada).
- **v4.9.9** - Otimização da busca binária de qualidade; correção de timeout e zombie processes.
