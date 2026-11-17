import { useId } from 'react';

// A drawn leaf with disease marks, used instead of real photos in this preview.
// Coordinates are on a 100 x 140 leaf.
//   spots   [x, y, radius, colour?]          round spots
//   marks   [x, y]                           scab-like squiggles
//   patches [x, y, rx, ry, colour]           blotches (mosaic, blight, dried tip), kept inside the leaf

const TONES = {
  green: { leaf: '#4f9f55', vein: '#6cb871', spot: '#8e391c' },
  hero: { leaf: '#5ba457', vein: '#7cbf72', spot: '#7a3517', halo: '#c2b046' },
};

const OUTLINE = 'M50 4C78 26 90 70 71 108C62 124 55 133 50 137C45 133 38 124 29 108C10 70 22 26 50 4Z';
const VEINS = 'M50 38 66 27M50 38 34 27M50 60 70 47M50 60 30 47M50 82 69 71M50 82 31 71M50 104 62 95M50 104 38 95';

export function LeafShape({ tone = 'green', spots = [], marks = [], patches = [] }) {
  const c = TONES[tone];
  const clipId = 'leaf' + useId().replace(/[^a-zA-Z0-9_-]/g, '');

  return (
    <g>
      <defs>
        <clipPath id={clipId}>
          <path d={OUTLINE} />
        </clipPath>
      </defs>
      <path d={OUTLINE} fill={c.leaf} />
      <g clipPath={`url(#${clipId})`}>
        {patches.map(([x, y, rx, ry, colour], i) => (
          <ellipse key={i} cx={x} cy={y} rx={rx} ry={ry} fill={colour} />
        ))}
      </g>
      <path d="M50 12V132" stroke={c.vein} strokeWidth="2.2" strokeLinecap="round" fill="none" />
      <path d={VEINS} stroke={c.vein} strokeWidth="1.4" strokeLinecap="round" fill="none" opacity="0.75" />
      {spots.map(([x, y, r, colour], i) => (
        <g key={i}>
          {c.halo && <circle cx={x} cy={y} r={r + 2} fill={c.halo} opacity="0.55" />}
          <circle cx={x} cy={y} r={r} fill={colour || c.spot} />
        </g>
      ))}
      {marks.map(([x, y], i) => (
        <path
          key={i}
          d={`M${x - 10} ${y} q5 -5.5 10 0 t10 0`}
          stroke="#36381f"
          strokeWidth="2.6"
          strokeLinecap="round"
          fill="none"
        />
      ))}
    </g>
  );
}

export default function Leaf({ label, className, ...shape }) {
  return (
    <svg
      viewBox="0 0 100 140"
      className={className}
      role={label ? 'img' : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      focusable="false"
    >
      <LeafShape {...shape} />
    </svg>
  );
}
