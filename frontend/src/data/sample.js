// Sample data for the home page preview. Later the list of diseases can come from the back end.

// How each disease is drawn (see components/Leaf.jsx).
const LOOK = {
  riceStemBorer: { patches: [[50, 70, 7, 46, '#dccfa4']], spots: [[50, 116, 3, '#6b4a2a']] },
  juteMosaic: {
    patches: [
      [38, 48, 10, 7, '#d6d14f'],
      [61, 62, 11, 8, '#d6d14f'],
      [42, 88, 10, 8, '#d6d14f'],
      [60, 104, 8, 6, '#d6d14f'],
      [57, 32, 6, 5, '#d6d14f'],
    ],
  },
  juteDieback: { patches: [[50, 8, 48, 34, '#8a5a2b'], [50, 42, 46, 7, '#b08a4c']] },
  blackGramYellowMosaic: {
    patches: [
      [42, 44, 15, 11, '#e3d23a'],
      [60, 76, 16, 12, '#e3d23a'],
      [40, 100, 12, 9, '#e3d23a'],
      [63, 40, 8, 6, '#e3d23a'],
    ],
  },
  potatoLateBlight: {
    patches: [
      [24, 80, 13, 21, '#c9c27a'],
      [24, 80, 9.5, 16, '#4a3820'],
      [75, 46, 11, 14, '#c9c27a'],
      [75, 46, 7.5, 10, '#55402a'],
    ],
  },
  appleScab: { marks: [[50, 60], [42, 92]], spots: [[63, 80, 3, '#3a3c22'], [36, 66, 2.6, '#3a3c22']] },
  pearLeafSpot: { spots: [[60, 44, 3], [41, 62, 3], [63, 76, 2.8], [47, 92, 3.2], [57, 106, 2.6]] },
  grapeLeafBlight: {
    spots: [
      [36, 50, 4, '#5b3a1e'],
      [58, 42, 3.5, '#5b3a1e'],
      [66, 64, 4.5, '#5b3a1e'],
      [40, 80, 4, '#5b3a1e'],
      [57, 90, 3.5, '#5b3a1e'],
      [46, 108, 3, '#5b3a1e'],
      [64, 100, 3.2, '#5b3a1e'],
      [30, 66, 3, '#5b3a1e'],
    ],
  },
};

// The 8 diseases the model knows.
export const DISEASES = [
  { crop: 'Rice', name: 'Stem borer', look: LOOK.riceStemBorer },
  { crop: 'Jute', name: 'Mosaic', look: LOOK.juteMosaic },
  { crop: 'Jute', name: 'Dieback', look: LOOK.juteDieback },
  { crop: 'Black gram', name: 'Yellow mosaic', look: LOOK.blackGramYellowMosaic },
  { crop: 'Potato', name: 'Late blight', look: LOOK.potatoLateBlight },
  { crop: 'Apple', name: 'Scab', look: LOOK.appleScab },
  { crop: 'Pear', name: 'Leaf spot', look: LOOK.pearLeafSpot },
  { crop: 'Grape', name: 'Leaf blight', look: LOOK.grapeLeafBlight },
];
