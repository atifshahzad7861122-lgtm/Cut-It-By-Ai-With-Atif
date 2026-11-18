import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface WordProps {
  text: string;
  startFrame: number;
  endFrame: number;
  highlight?: boolean;
}

export const SpringWord: React.FC<WordProps> = ({
  text,
  startFrame,
  endFrame,
  highlight = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // If outside frame range, return null
  if (frame < startFrame || frame > endFrame + 10) {
    return null;
  }

  // Spring physics for punchy bounce
  const enterProgress = spring({
    frame: frame - startFrame,
    fps,
    config: {
      damping: 10,
      mass: 0.5,
      stiffness: 180,
    },
  });

  const scale = interpolate(enterProgress, [0, 1], [0.75, 1.08]);
  const opacity = interpolate(frame - startFrame, [0, 3], [0, 1], {
    extrapolateRight: "clamp",
  });
  const rotation = interpolate(enterProgress, [0, 0.5, 1], [-4, 3, 0]);

  const activeColor = highlight ? "#FFE600" : "#00F0FF";
  const glowColor = highlight
    ? "rgba(255, 230, 0, 0.7)"
    : "rgba(0, 240, 255, 0.7)";

  return (
    <span
      style={{
        display: "inline-block",
        margin: "0 10px",
        transform: `scale(${scale}) rotate(${rotation}deg)`,
        opacity,
        color: activeColor,
        textShadow: `0 0 20px ${glowColor}, 0 4px 10px rgba(0,0,0,0.9)`,
        WebkitTextStroke: "2.5px #000000",
        fontWeight: 900,
        textTransform: "uppercase",
        letterSpacing: "1px",
      }}
    >
      {text}
    </span>
  );
};
