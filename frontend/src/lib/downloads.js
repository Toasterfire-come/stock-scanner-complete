import { toast } from "sonner";

export function downloadBlob(blob, filename) {
  try {
    if (!(blob instanceof Blob)) {
      const asBlob = new Blob([blob], { type: 'application/octet-stream' });
      blob = asBlob;
    }
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || `download-${Date.now()}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    return true;
  } catch (e) {
    toast.error('Download failed');
    return false;
  }
}

export async function tryParseBlobJson(blob) {
  try {
    if (!(blob instanceof Blob)) return null;
    const text = await blob.text();
    if (!text) return null;
    try { return JSON.parse(text); } catch { return null; }
  } catch { return null; }
}

export function estimateCsvSizeBytes(rowCount, columns = 8) {
  const avgCellBytes = 12; // rough average including comma and quotes
  const newlineBytes = 1;
  const headerBytes = columns * (avgCellBytes + 1) + newlineBytes;
  const rowBytes = (columns * (avgCellBytes + 1)) + newlineBytes;
  return Math.max(0, headerBytes + (Math.max(0, rowCount) * rowBytes));
}
