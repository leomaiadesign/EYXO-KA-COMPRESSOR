figma.showUI(__html__, { width: 400, height: 600 });

function getExportableFrames() {
  return figma.currentPage.children.filter(node => 
    node.type === 'FRAME' || node.type === 'COMPONENT' || node.type === 'INSTANCE'
  );
}

const frames = getExportableFrames();
const initialList = frames.map(node => ({
  id: node.id,
  name: node.name
}));
figma.ui.postMessage({ type: 'initial-list', items: initialList });

function getExportSettingForNode(node) {
  let setting = { format: 'PNG' };
  if (node.exportSettings && node.exportSettings.length > 0) {
    // Procura por uma configuração PNG, ou pega a primeira disponível e ajusta para PNG
    const pngSetting = node.exportSettings.find(s => s.format === 'PNG') || node.exportSettings[0];
    if (pngSetting && pngSetting.constraint) {
      setting.constraint = pngSetting.constraint;
    }
  }
  return setting;
}

async function calculateSizes() {
  for (const node of frames) {
    try {
      const fullBytes = await node.exportAsync(getExportSettingForNode(node));
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

calculateSizes();

figma.ui.onmessage = async (msg) => {
  if (msg.type === 'compress-selected') {
    const toCompressReqs = msg.toCompress || [];
    const toKeepReqs = msg.toKeep || [];
    
    if (toCompressReqs.length === 0) {
      figma.ui.postMessage({ type: 'error', message: 'Nenhuma arte marcada para comprimir.' });
      return;
    }
    
    const compressedImages = [];
    const originalImages = [];
    
    // Processar os que vão ser comprimidos
    for (const req of toCompressReqs) {
      const node = figma.getNodeById(req.id);
      if (node) {
        try {
          const bytes = await node.exportAsync(getExportSettingForNode(node));
          compressedImages.push({
            id: node.id,
            name: node.name.replace(/[^a-z0-9]/gi, '_').toLowerCase(),
            bytes: bytes,
            original_size: bytes.length,
            target_kb: req.targetKb
          });
        } catch (e) {}
      }
    }
    
    // Processar os que vão ser mantidos intactos (não marcados)
    for (const req of toKeepReqs) {
      const node = figma.getNodeById(req.id);
      if (node) {
        try {
          const bytes = await node.exportAsync(getExportSettingForNode(node));
          originalImages.push({
            id: node.id,
            name: node.name.replace(/[^a-z0-9]/gi, '_').toLowerCase(),
            bytes: bytes,
            original_size: bytes.length
          });
        } catch (e) {}
      }
    }
    
    figma.ui.postMessage({ 
        type: 'selection-bytes-ready', 
        compressedImages: compressedImages,
        originalImages: originalImages
    });
  }

  if (msg.type === 'cancel') {
    figma.closePlugin();
  }
};
