// Photo helpers that run in the browser.

export const MAX_UPLOAD_BYTES = 10 * 1024 * 1024; // the back end's limit
const SHRINK_OVER_PX = 2048;
const SHRINK_OVER_BYTES = 5 * 1024 * 1024;
const THUMB_PX = 160;

const PHOTO_EXT = /\.(jpe?g|png|webp|heic|heif)$/i;

// Is this file a photo SafeCrop can take? (HEIC from iPhones often has an empty type on Windows, so the
// name is checked too.) The back end checks again by looking inside the file.
export function looksLikePhoto(file) {
  return (file.type && file.type.startsWith('image/')) || PHOTO_EXT.test(file.name || '');
}

// Open the photo in the browser, turned the right way up (EXIF). Returns null when the browser can't open it
// (for example HEIC in Chrome): then the original file is sent and the back end opens it.
async function openPhoto(file) {
  try {
    return await createImageBitmap(file, { imageOrientation: 'from-image' });
  } catch {
    return null;
  }
}

function canvasBlob(canvas, quality) {
  return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', quality));
}

// Shrink only when the photo is bigger than 2048 pixels or 5 MB (shrinking adds compression, which could change the
// photo check, so small photos are sent untouched). Returns { file, shrunk, width, height }.
export async function preparePhoto(file) {
  const bitmap = await openPhoto(file);
  if (!bitmap) return { file, shrunk: false, width: 0, height: 0 };
  const { width, height } = bitmap;
  const longest = Math.max(width, height);
  if (longest <= SHRINK_OVER_PX && file.size <= SHRINK_OVER_BYTES) {
    bitmap.close();
    return { file, shrunk: false, width, height };
  }
  const scale = Math.min(1, SHRINK_OVER_PX / longest);
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(width * scale);
  canvas.height = Math.round(height * scale);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff'; // see-through parts of a PNG become white, not black
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close();
  const blob = await canvasBlob(canvas, 0.92);
  if (!blob) return { file, shrunk: false, width, height };
  const name = (file.name || 'photo').replace(/\.[^.]+$/, '') + '.jpg';
  return { file: new File([blob], name, { type: 'image/jpeg' }), shrunk: true, width: canvas.width, height: canvas.height };
}

// A small square JPEG (the middle of the photo, like the back end uses) for History. null if the browser can't
// open the photo.
export async function makeThumbnail(file) {
  const bitmap = await openPhoto(file);
  if (!bitmap) return null;
  const side = Math.min(bitmap.width, bitmap.height);
  const canvas = document.createElement('canvas');
  canvas.width = THUMB_PX;
  canvas.height = THUMB_PX;
  const ctx = canvas.getContext('2d');
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(bitmap, (bitmap.width - side) / 2, (bitmap.height - side) / 2, side, side, 0, 0, THUMB_PX, THUMB_PX);
  bitmap.close();
  return canvas.toDataURL('image/jpeg', 0.72);
}

export function formatBytes(n) {
  return n >= 1024 * 1024 ? (n / 1024 / 1024).toFixed(1) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB';
}
