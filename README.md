# ✂️ EYXO | KA Compressor

**Compressão inteligente de PNG com preservação de transparência, direto no Figma**

---

## O que faz

- Comprime frames e imagens PNG com alvo de peso exato (ex: 200KB)
- Preserva alpha/transparência total (RGBA) com suavização avançada de gradientes
- Processa 100% local — nenhum arquivo sai da sua máquina

## Como instalar

1. No Figma Desktop, vá em `Plugins` → `Development` → `Import plugin from manifest...`
2. Selecione o arquivo `manifest.json` localizado na pasta do plugin
3. O plugin já estará pronto para uso!

## Como usar

1. Abra o plugin em qualquer página do Figma
2. Todos os frames da página aparecerão listados automaticamente
3. Marque quais frames comprimir e defina o alvo máximo de KB para cada um
4. Clique em **COMPRIMIR SELEÇÃO**
5. Você poderá baixar o pacote final completo (`.zip`) ou cada imagem individualmente

---

## Tecnologia

- **Motor de Compressão:** Quantização de cores (*Median-Cut*) executada via `UPNG.js`, combinada com um algoritmo construído nativamente de **Floyd-Steinberg Dithering** para garantir sombras e degradês perfeitos, sem marcas de *banding*.
- **Pacote:** Utiliza `pako.js` para otimização rápida e geração do `.zip`.
- **Segurança:** Zero permissões obscuras, zero upload de imagens, funciona totalmente offline na interface do Figma.

---

## Suporte

Encontrou algum bug ou erro na compressão? 
Me chame no Discord: **`leomaia.eyxo`**

---

## Histórico (Changelog)

- **v5.2.0** - Refatoração Arquitetural: Remoção completa das dependências externas (CDNs). As bibliotecas matemáticas e de compressão agora estão 100% embutidas no plugin, garantindo que ele funcione perfeitamente de forma nativa e *offline* em qualquer rede corporativa (EYXO) sem bloqueios de *firewall*.
- **v5.1.4** - Hotfix: Correção final do *crash* silencioso causado por incompatibilidade de tipos (`ArrayBuffer` vs `Uint8Array`) que forçava o plugin a exportar imagens destruídas com apenas 8 cores.
- **v5.1.3** - Hotfix: Correção crítica na requantização do dithering que estava distorcendo as cores (cores invertidas/sépia).

