# ✂️ EYXO | KA Compressor

**Otimização inteligente de imagens sem perda de qualidade visual e transparência.**

🌐 **Acesso à ferramenta:** [eyxo-ka-compressor.onrender.com](https://eyxo-ka-compressor.onrender.com/)

---

## 🚀 O Desafio
No fluxo de aprovação e entrega de peças de Key Accounts (KA), o envio de imagens frequentemente esbarra em restrições rígidas de peso (KB/MB) impostas pelas plataformas dos clientes. Ferramentas genéricas de compressão na internet costumam destruir a resolução original, alterar as cores da marca ou, pior, remover a transparência (fundo vazado) que é essencial para o layout final.

Além disso, há um fator crítico: **confidencialidade**. Subir campanhas não lançadas em sites gratuitos de compressão expõe o material dos clientes a servidores de terceiros e possíveis vazamentos.

## 💡 A Solução
O **KA Compressor** foi desenvolvido internamente como uma ferramenta sob medida para resolver esse gargalo operacional com total segurança. Ele aplica um algoritmo de *quantização de cores dinâmico* que reduz drasticamente o peso do arquivo PNG, garantindo que a transparência seja mantida e a percepção visual fique idêntica à arte original.

## 🔒 Segurança e Privacidade (Privacy-First)
Este é o diferencial de ouro da nossa arquitetura. Lidando com marcas globais, o vazamento de peças antes do lançamento oficial é um risco inaceitável.
- **Ambiente Isolado:** Ao contrário de ferramentas públicas (TinyPNG, ILoveIMG), as imagens nunca são armazenadas em bancos de dados de terceiros ou usadas para treinar IAs.
- **Auto-destruição (Limpeza Automática):** O servidor possui uma rotina rigorosa de segurança que varre e destrói permanentemente todos os arquivos e lotes processados após um curto período de tempo (1 hora). 
- **Garantia de Sigilo:** O tráfego e o processamento são efêmeros, garantindo que nenhum material confidencial fique exposto ou salvo na internet.

## ✨ Principais Funcionalidades
- **Compressão Sob Medida (Target KB):** Defina exatamente o limite de peso (KB) que a plataforma do cliente exige. O sistema fará testes iterativos na imagem até alcançar o alvo sem perder a nitidez.
- **Preservação de Transparência (RGBA):** Total suporte a PNGs com fundo vazado, mantendo as camadas Alpha intactas.
- **Interface Premium (Dark Mode):** Layout moderno e focado na experiência do usuário, sem distrações.
- **Pré-visualização Inteligente:** Galeria de imagens dispostas em um grid dinâmico que lê e respeita a proporção real de cada arte.
- **Exportação Ágil:** Ao final do processo, baixe suas imagens empacotadas automaticamente em um `.zip` ou baixe a imagem avulsa com um único clique.

## 🛠️ Tecnologias Utilizadas
- **Core / Backend:** Python + Flask
- **Processamento Gráfico:** Pillow (PIL)
- **Frontend:** HTML5, CSS3, Vanilla JS
- **Infraestrutura:** Deploy contínuo via Docker + Render (Garante pacotes de sistema nativos)

---

## 🔄 Últimas Atualizações (Changelog)

- **v4.6.3** - Correção Crítica (Erro 502): Ajustados os tempos de limite (Timeout) e otimizada a velocidade do `pngquant` e `Pillow` para consumir menos CPU/RAM, evitando quedas no servidor Render.
- **v4.6.2** - Deploy / Infraestrutura: Adicionado suporte nativo a Docker (`Dockerfile`) para garantir a instalação automática do `pngquant` no servidor de produção (Render).
- **v4.6.1** - Organização de Projeto: Limpeza estrutural da pasta, remoção de arquivos órfãos, exclusão de scripts de teste antigos e correção no script de limpeza de cache de imagens.
