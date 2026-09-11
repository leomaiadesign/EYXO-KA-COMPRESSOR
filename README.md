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

## 🎨 Plugin para Figma (Versão Experimental)
Agora você pode usar o compressor direto de dentro do Figma sem precisar acessar o site! A compressão é feita pelo nosso servidor, mas tudo acontece na sua tela do Figma.

📥 **[Download do Plugin (.zip)](https://github.com/leomaiadesign/EYXO-KA-COMPRESSOR/releases/download/latest/EYXO-KA-Compressor-Figma.zip)**

**Como instalar no Figma:**
1. Baixe o arquivo `.zip` acima e extraia no seu computador.
2. Abra o aplicativo Figma Desktop.
3. Vá no menu: `Plugins` > `Development` > `Import plugin from manifest...`
4. Selecione o arquivo `manifest.json` que está dentro da pasta extraída.
5. Pronto! Basta selecionar uma arte, abrir o plugin e comprimir!

## 🛠️ Tecnologias Utilizadas
- **Core / Backend:** Python + Flask
- **Processamento Gráfico:** Pillow (PIL)
- **Frontend:** HTML5, CSS3, Vanilla JS
- **Infraestrutura:** Deploy contínuo via Docker + Render (Garante pacotes de sistema nativos)

---

## 🔄 Últimas Atualizações (Changelog)

- **v4.9.8** - UX: Ajustado o valor padrão do seletor dropdown para iniciar em 200 KB.
- **v4.9.7** - UX: Substituição do campo de limite livre por um seletor (dropdown) com valores pré-definidos (100 KB, 200 KB, 500 KB) garantindo maior estabilidade no processo.
- **v4.9.6** - Performance e Qualidade: implementada Busca Binária (Binary Search) para encontrar o "ponto doce" da compressão em no máximo 4 tentativas, eliminando reduções desnecessárias.
