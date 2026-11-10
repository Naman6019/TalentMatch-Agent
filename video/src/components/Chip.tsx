import React from "react";
import { C } from "../theme";

export const Chip: React.FC<{ color?: string; children: React.ReactNode; size?: number; style?: React.CSSProperties }> = ({
  color = C.cyan,
  children,
  size = 26,
  style,
}) => (
  <span
    style={{
      display: "inline-block",
      padding: `${size * 0.28}px ${size * 0.6}px`,
      borderRadius: 999,
      fontSize: size,
      fontWeight: 600,
      color,
      background: `${color}1F`,
      border: `1.5px solid ${color}66`,
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {children}
  </span>
);
