import type { ReactNode } from "react";
import type { RinkPoint } from "../types/prescout";

interface RinkProps {
  points?: RinkPoint[];
  children?: ReactNode;
  className?: string;
}

const mapX = (x: number) => x + 100;
const mapY = (y: number) => y + 42.5;

export function FullRink({ points = [], children, className = "" }: RinkProps) {
  return (
    <svg viewBox="0 0 200 85" className={className} aria-label="Full rink diagram">
      <rect x="1" y="1" width="198" height="83" rx="15" className="rink-surface" />
      <line x1="100" y1="1" x2="100" y2="84" className="rink-red" />
      <circle cx="100" cy="42.5" r="10" className="rink-red" fill="none" />
      <line x1="64" y1="2" x2="64" y2="83" className="rink-blue" />
      <line x1="136" y1="2" x2="136" y2="83" className="rink-blue" />
      <line x1="11" y1="13" x2="11" y2="72" className="rink-red" />
      <line x1="189" y1="13" x2="189" y2="72" className="rink-red" />
      {points.map((point, index) => (
        <circle
          key={`${point.x}-${point.y}-${index}`}
          cx={mapX(point.x)}
          cy={mapY(point.y)}
          r={1.5 + point.danger * 0.65}
          className="rink-dot"
        />
      ))}
      {children}
    </svg>
  );
}

export function HalfRink({ points = [], className = "" }: RinkProps) {
  return (
    <svg viewBox="0 0 100 85" className={className} aria-label="Half rink diagram">
      <path d="M0 1H85A14 14 0 0 1 99 15V70A14 14 0 0 1 85 84H0Z" className="rink-surface" />
      <line x1="36" y1="2" x2="36" y2="83" className="rink-blue" />
      <line x1="89" y1="14" x2="89" y2="71" className="rink-red" />
      <path d="M89 35 Q78 42.5 89 50" className="rink-red" fill="none" />
      <circle cx="67" cy="22" r="2.7" className="rink-mark" />
      <circle cx="67" cy="63" r="2.7" className="rink-mark" />
      {points.filter((point) => point.x >= 0).map((point, index) => (
        <circle
          key={`${point.x}-${point.y}-${index}`}
          cx={point.x}
          cy={mapY(point.y)}
          r={1.5 + point.danger * 0.7}
          className="rink-dot"
        />
      ))}
    </svg>
  );
}

interface NetFrontProps {
  zones: Array<{ label: string; x: number; y: number; value: string }>;
  className?: string;
}

export function NetFront({ zones, className = "" }: NetFrontProps) {
  return (
    <svg viewBox="0 0 100 70" className={className} aria-label="Net front save percentage diagram">
      <path d="M20 58 Q20 8 50 5 Q80 8 80 58Z" className="rink-crease" />
      <path d="M34 60V24H66V60" className="rink-net" />
      <line x1="34" y1="42" x2="66" y2="42" className="rink-net-soft" />
      {zones.map((zone) => (
        <g key={zone.label}>
          <circle cx={zone.x} cy={zone.y} r="10" className="rink-zone" />
          <text x={zone.x} y={zone.y - 1} textAnchor="middle" className="rink-zone-value">{zone.value}</text>
          <text x={zone.x} y={zone.y + 5} textAnchor="middle" className="rink-zone-label">{zone.label}</text>
        </g>
      ))}
    </svg>
  );
}
