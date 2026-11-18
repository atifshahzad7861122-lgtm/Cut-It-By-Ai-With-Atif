import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Equalizer } from "./Equalizer";
import { SpringWord } from "./SpringWord";

export interface ClipProps {
  hookText?: string;
  brandName?: string;
  showWatermark?: boolean;
  words?: Array<{ text: string; s: number; e: number; highlight?: boolean }>;
}

export const AnimatedClip: React.FC<ClipProps> = ({
  hookText = "WAIT FOR THE UNBELIEVABLE MOMENT!",
  brandName = "Cut it by Ai",
  showWatermark = false,
  words = [
    { text: "LOOK", s: 0.2, e: 0.7, highlight: false },
    { text: "AT", s: 0.7, e: 1.1, highlight: false },
    { text: "THIS", s: 1.1, e: 1.6, highlight: true },
    { text: "INSANE", s: 1.6, e: 2.2, highlight: true },
    { text: "HIGHLIGHT", s: 2.2, e: 3.0, highlight: false },
    { text: "LIVE", s: 3.0, e: 3.6, highlight: true },
  ],
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  // Hook Title Spring Animation
  const hookSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 200 },
  });
  const hookScale = interpolate(hookSpring, [0, 1], [0.5, 1]);
  const hookOpacity = interpolate(hookSpring, [0, 1], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0F0B09",
        fontFamily: "'Poppins', sans-serif",
        overflow: "hidden",
      }}
    >
      {/* Ambient Animated Glow Mesh */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "10%",
          width: "800px",
          height: "800px",
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(255, 139, 51, 0.2) 0%, transparent 70%)",
          filter: "blur(60px)",
          transform: `translateY(${Math.sin(frame * 0.05) * 40}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "20%",
          right: "5%",
          width: "700px",
          height: "700px",
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(0, 240, 255, 0.15) 0%, transparent 70%)",
          filter: "blur(60px)",
          transform: `translateY(${Math.cos(frame * 0.04) * 35}px)`,
        }}
      />

      {/* Top Hook Banner */}
      <div
        style={{
          position: "absolute",
          top: "140px",
          width: "100%",
          display: "flex",
          justifyContent: "center",
          transform: `scale(${hookScale})`,
          opacity: hookOpacity,
          zIndex: 10,
        }}
      >
        <div
          style={{
            background: "rgba(255, 255, 255, 0.95)",
            border: "4px solid #FF8B33",
            boxShadow:
              "0 16px 40px rgba(0, 0, 0, 0.6), 0 0 25px rgba(255, 139, 51, 0.4)",
            borderRadius: "24px",
            padding: "20px 48px",
            color: "#181419",
            fontSize: "44px",
            fontWeight: 900,
            textTransform: "uppercase",
            letterSpacing: "1.5px",
            textAlign: "center",
            maxWidth: "880px",
          }}
        >
          {hookText}
        </div>
      </div>

      {/* Main Kinetic Captions Zone */}
      <div
        style={{
          position: "absolute",
          bottom: "38%",
          width: "100%",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flexWrap: "wrap",
          padding: "0 40px",
          fontSize: "68px",
          zIndex: 15,
        }}
      >
        {words.map((w, idx) => (
          <SpringWord
            key={idx}
            text={w.text}
            startFrame={Math.round(w.s * fps)}
            endFrame={Math.round(w.e * fps)}
            highlight={w.highlight}
          />
        ))}
      </div>

      {/* Audio Visualizer Equalizer */}
      <div
        style={{
          position: "absolute",
          bottom: "160px",
          width: "100%",
          zIndex: 8,
        }}
      >
        <Equalizer bars={32} color="#FF8B33" />
      </div>

      {/* Brand Pill Footer */}
      <div
        style={{
          position: "absolute",
          bottom: "60px",
          width: "100%",
          display: "flex",
          justifyContent: "center",
          zIndex: 10,
        }}
      >
        <div
          style={{
            background: "rgba(255, 255, 255, 0.12)",
            backdropFilter: "blur(16px)",
            border: "1px solid rgba(255, 255, 255, 0.25)",
            borderRadius: "999px",
            padding: "10px 28px",
            color: "#FFFFFF",
            fontSize: "22px",
            fontWeight: 700,
            letterSpacing: "1px",
            textTransform: "uppercase",
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.3)",
          }}
        >
          ⚡ {brandName}
        </div>
      </div>

      {/* Exported Clips Watermark: white icon only, 40% opacity, bottom-right, 48px margin */}
      {showWatermark && (
        <div
          style={{
            position: "absolute",
            bottom: "48px",
            right: "48px",
            width: "56px",
            height: "56px",
            opacity: 0.4,
            zIndex: 30,
            pointerEvents: "none",
          }}
        >
          <svg viewBox="0 0 1024 1024" width="56" height="56">
            <defs>
              <clipPath id="wm-clip-top">
                <polygon points="-688.7,1380.4 1768.7,-340.4 908.4,-1569.1 -1549.1,151.6" />
              </clipPath>
              <clipPath id="wm-clip-bot">
                <polygon points="-688.7,1380.4 1768.7,-340.4 2629.1,888.4 171.6,2609.1" />
              </clipPath>
            </defs>
            <rect width="1024" height="1024" rx="230" fill="none" stroke="#FFFFFF" strokeWidth="64" />
            <g transform="translate(-7.5,-10.6)">
              <g clipPath="url(#wm-clip-top)">
                <path d="M372,318 L372,722 L742,520 Z" fill="#fff" stroke="#fff" strokeWidth="56" strokeLinejoin="round" />
              </g>
            </g>
            <g transform="translate(7.5,10.6)">
              <g clipPath="url(#wm-clip-bot)">
                <path d="M372,318 L372,722 L742,520 Z" fill="#fff" stroke="#fff" strokeWidth="56" strokeLinejoin="round" />
              </g>
            </g>
            <path d="M800,196 Q806,262 872,268 Q806,274 800,340 Q794,274 728,268 Q794,262 800,196 Z" fill="#fff" />
          </svg>
        </div>
      )}
    </AbsoluteFill>
  );
};
