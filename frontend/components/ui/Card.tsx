"use client";

import { ReactNode } from "react";
import { classNames } from "../../lib/utils";

interface CardProps {
  children: ReactNode;
  className?: string;
  padding?: "none" | "sm" | "md" | "lg";
}

export default function Card({ children, className, padding = "md" }: CardProps) {
  const paddingStyles = {
    none: "",
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  return (
    <div className={classNames("bg-white rounded-lg shadow", paddingStyles[padding], className)}>
      {children}
    </div>
  );
}
