import React from "react";
import { Composition } from "remotion";
import { AnimatedClip } from "./AnimatedClip";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AnimatedClip"
        component={AnimatedClip}
        durationInFrames={150} // 5 seconds at 30 fps
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          hookText: "WAIT FOR THE UNBELIEVABLE MOMENT!",
          brandName: "Cut it by Ai With Atif",
        }}
      />
    </>
  );
};
