figma.showUI(__html__, { width: 340, height: 480 });

figma.ui.onmessage = async (msg) => {
  if (msg.type === 'get-selection') {
    const selection = figma.currentPage.selection;
    if (selection.length === 0) {
      figma.ui.postMessage({ type: 'error', message: 'Nenhuma arte selecionada.' });
      return;
    }
    
    // Suporte para múltiplas seleções
    const images = [];
    
    for (const node of selection) {
      try {
        const bytes = await node.exportAsync({ format: 'PNG' });
        images.push({
          name: node.name.replace(/[^a-z0-9]/gi, '_').toLowerCase(),
          bytes: bytes,
          width: node.width,
          height: node.height
        });
      } catch (e) {
        figma.ui.postMessage({ type: 'error', message: `Erro ao exportar a arte ${node.name}.` });
        return;
      }
    }
    
    figma.ui.postMessage({ type: 'selection-ready', images: images });
  }

  if (msg.type === 'cancel') {
    figma.closePlugin();
  }
};
