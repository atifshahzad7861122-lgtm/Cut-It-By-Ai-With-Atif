import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export const Equalizer: React.FC<{ bars?: number; color?: string }> = ({
  bars = 24,
  color = "#FF8B33",
}) => {
  const frame = useCurrentFrame();

  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "center",
        gap: "4px",
        height: "60px",
      }}
    >
      {Array.from({ length: bars }).map((_, i) => {
        const speed = 0.15 + (i % 5) * 0.04;
        const wave = Math.sin(frame * speed + i);
        const height = interpolate(wave, [-1, 1], [10, 52]);

        return (
          <div
            key={i}
            style={{
              width: "6px",
              height: `${height}px`,
              borderRadius: "4px",
              background: `linear-gradient(to top, ${color}, #FFAE5D)`,
              boxShadow: `0 0 10px ${color}88`,
              transition: "height 0.05s ease",
            }}
          />
        );
      })}
    </div>
  );
};
