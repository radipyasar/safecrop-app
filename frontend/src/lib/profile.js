// The farmer's profile and this device's id, kept in the browser (localStorage). Nothing here goes to the server
// except the device id, which is sent with each check so the server log can count checks per device.

const PROFILE_KEY = 'safecrop.profile';
const DEVICE_KEY = 'safecrop.deviceId';

export const EMPTY_PROFILE = { name: '', district: '', crops: [], otherCrops: '', lang: 'en' };

export function getProfile() {
  try {
    const saved = JSON.parse(localStorage.getItem(PROFILE_KEY) || 'null');
    return saved ? { ...EMPTY_PROFILE, ...saved } : { ...EMPTY_PROFILE };
  } catch {
    return { ...EMPTY_PROFILE };
  }
}

export function saveProfile(profile) {
  const clean = {
    name: String(profile.name || '').trim().slice(0, 60),
    district: String(profile.district || '').trim().slice(0, 60),
    crops: Array.isArray(profile.crops) ? profile.crops : [],
    otherCrops: String(profile.otherCrops || '').trim().slice(0, 120),
    lang: profile.lang === 'bn' ? 'bn' : 'en',
  };
  localStorage.setItem(PROFILE_KEY, JSON.stringify(clean));
  return clean;
}

// A random id made once per browser (not linked to the person).
export function getDeviceId() {
  try {
    let id = localStorage.getItem(DEVICE_KEY);
    if (!id) {
      id = crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2);
      localStorage.setItem(DEVICE_KEY, id);
    }
    return id;
  } catch {
    return 'no-storage';
  }
}
