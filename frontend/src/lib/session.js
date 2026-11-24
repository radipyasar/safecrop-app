// Things kept only in memory while the tab is open (gone after a refresh, never saved anywhere):
// - the photo dropped on the home page, picked up by the Check page
// - the photo of each check, so the Result page can send it again with the advice request

let pendingPhoto = null;
const photosByCheck = new Map();

export function setPendingPhoto(file) {
  pendingPhoto = file;
}

export function takePendingPhoto() {
  const file = pendingPhoto;
  pendingPhoto = null;
  return file;
}

export function rememberPhoto(checkId, file) {
  photosByCheck.set(checkId, file);
  while (photosByCheck.size > 5) photosByCheck.delete(photosByCheck.keys().next().value);
}

export function photoFor(checkId) {
  return photosByCheck.get(checkId) || null;
}

export function forgetPhoto(checkId) {
  photosByCheck.delete(checkId);
}
