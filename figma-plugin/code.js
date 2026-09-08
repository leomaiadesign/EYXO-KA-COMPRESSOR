figma.showUI(__html__, { width: 400, height: 600 });

// Pega todos os frames exportáveis da página (Frames, Componentes, Instâncias)
function getExportableFrames() {
  return figma.currentPage.children.filter(node => 
    node.type === 'FRAME' || node.type === 'COMPONENT' || node.type === 'INSTANCE'
  );
}

// 1. Enviar lista inicial imediatamente para a UI
const frames = getExportableFrames();
const initialList = frames.map(node => ({
  id: node.id,
  name: node.name
}));
figma.ui.postMessage({ type: 'initial-list', items: initialList });

// 2. Exportar silenciosamente para descobrir os tamanhos (KB) e gerar thumbnails
async function calculateSizes() {
  for (const node of frames) {
    try {
      // Exporta em tamanho real apenas para ver o peso, mas não devolve pra UI (pesado)
      const fullBytes = await node.exportAsync({ format: 'PNG' });
      
      // Exporta uma miniatura rápida (scale 0.1 ou largura fixa de 100) para mostrar na tela inicial
      const thumbBytes = await node.exportAsync({ format: 'PNG', constraint: { type: 'SCALE', value: 0.1 } });
      
      figma.ui.postMessage({ 
        type: 'size-update', 
        id: node.id, 
        size: fullBytes.length,
        thumbBytes: thumbBytes,
        width: node.width,
        height: node.height
      });
    } catch (e) {
      figma.ui.postMessage({ type: 'size-error', id: node.id });
    }
  }
}

// Inicia o cálculo de peso invisivelmente
calculateSizes();

// 3. Ouve as requisições da UI
figma.ui.onmessage = async (msg) => {
  if (msg.type === 'compress-selected') {
    const selectedRequests = msg.requests; // Array de { id, targetKb }
    
    if (selectedRequests.length === 0) {
      figma.ui.postMessage({ type: 'error', message: 'Nenhuma arte marcada.' });
      return;
    }
    
    const images = [];
    
    for (const req of selectedRequests) {
      const node = figma.getNodeById(req.id);
      if (node) {
        try {
          const bytes = await node.exportAsync({ format: 'PNG' });
          images.push({
            id: node.id,
            name: node.name.replace(/[^a-z0-9]/gi, '_').toLowerCase(),
            bytes: bytes,
            original_size: bytes.length,
            target_kb: req.targetKb
          });
        } catch (e) {
          figma.ui.postMessage({ type: 'error', message: `Erro ao processar a arte ${node.name}.` });
          return;
        }
      }
    }
    
    figma.ui.postMessage({ type: 'selection-bytes-ready', images: images });
  }

  if (msg.type === 'cancel') {
    figma.closePlugin();
  }
};
