import React, { useId } from "react";

type MarkProps = { size?: number; withSpark?: boolean; className?: string };

export function LogoMark({ size = 40, withSpark = true, className }: MarkProps) {
  const uid = useId().replace(/:/g, "");
  const bg = `bg-${uid}`;
  const top = `top-${uid}`;
  const bot = `bot-${uid}`;
  const tri = "M372,318 L372,722 L742,520 Z";

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 1024 1024"
      width={size}
      height={size}
      className={className}
      role="img"
      aria-label="Cut it by Ai"
    >
      <defs>
        <linearGradient id={bg} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#FFA23A" />
          <stop offset="1" stopColor="#FF5A00" />
        </linearGradient>
        <clipPath id={top}>
          <polygon points="-688.7,1380.4 1768.7,-340.4 908.4,-1569.1 -1549.1,151.6" />
        </clipPath>
        <clipPath id={bot}>
          <polygon points="-688.7,1380.4 1768.7,-340.4 2629.1,888.4 171.6,2609.1" />
        </clipPath>
      </defs>

      <rect width="1024" height="1024" rx="230" fill={`url(#${bg})`} />

      {/* upper half of the play button */}
      <g transform="translate(-7.5,-10.6)">
        <g clipPath={`url(#${top})`}>
          <path d={tri} fill="#fff" stroke="#fff" strokeWidth="56" strokeLinejoin="round" />
        </g>
      </g>

      {/* lower half of the play button */}
      <g transform="translate(7.5,10.6)">
        <g clipPath={`url(#${bot})`}>
          <path d={tri} fill="#fff" stroke="#fff" strokeWidth="56" strokeLinejoin="round" />
        </g>
      </g>

      {/* AI spark */}
      {withSpark && (
        <path
          d="M800,196 Q806,262 872,268 Q806,274 800,340 Q794,274 728,268 Q794,262 800,196 Z"
          fill="#fff"
        />
      )}
    </svg>
  );
}

type LockupProps = {
  size?: number; // icon height in px
  theme?: "dark" | "light"; // dark = used on dark backgrounds (white text)
  showTagline?: boolean;
  className?: string;
};

export function LogoLockup({
  size = 36,
  theme = "dark",
  showTagline = true,
  className,
}: LockupProps) {
  const ink = theme === "dark" ? "#FFFFFF" : "#1E140E";
  const muted = theme === "dark" ? "#C9B8AA" : "#7A6354";

  return (
    <div
      className={className}
      style={{ display: "flex", alignItems: "center", gap: size * 0.28 }}
    >
      <LogoMark size={size} />
      <div style={{ display: "flex", flexDirection: "column", lineHeight: 1 }}>
        <span
          style={{
            fontFamily: "Inter, system-ui, sans-serif",
            fontWeight: 700,
            fontSize: size * 0.5,
            letterSpacing: "-0.03em",
            color: ink,
            whiteSpace: "nowrap",
          }}
        >
          Cut it <span style={{ color: "#FF7A1A" }}>by Ai</span>
        </span>
        {showTagline && (
          <span
            style={{
              fontFamily: "Inter, system-ui, sans-serif",
              fontWeight: 600,
              fontSize: Math.max(8, size * 0.2),
              letterSpacing: "0.3em",
              color: muted,
              marginTop: size * 0.12,
            }}
          >
            WITH ATIF
          </span>
        )}
      </div>
    </div>
  );
}

export function Logo({
  collapsed = false,
  size = 36,
  theme = "dark",
}: {
  collapsed?: boolean;
  size?: number;
  theme?: "dark" | "light";
}) {
  return collapsed ? (
    <LogoMark size={size} />
  ) : (
    <LogoLockup size={size} theme={theme} />
  );
}
export default Logo;
