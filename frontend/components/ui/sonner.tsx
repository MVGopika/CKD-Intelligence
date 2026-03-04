"use client";

import { useTheme } from "next-themes";
import { Toaster as Sonner, ToasterProps } from "sonner";
import React from "react";

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme();

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      position="top-center" // top position
      expand={true}
      richColors
      toastOptions={{
        classNames: {
          toast: `
            rounded-xl shadow-lg border text-sm font-medium
            px-4 py-3 flex items-center gap-2 transition-all duration-300

            /* Light Mode Base */
            data-[theme=light]:bg-white
            data-[theme=light]:text-black
            data-[theme=light]:border-black

            /* Dark Mode Base */
            data-[theme=dark]:bg-black
            data-[theme=dark]:text-white
            data-[theme=dark]:border-white

            /* Success */
            data-[type=success]:bg-green-600
            data-[type=success]:text-white

            /* Error */
            data-[type=error]:bg-red-600
            data-[type=error]:text-white

            /* Warning */
            data-[type=warning]:bg-yellow-500
            data-[type=warning]:text-black

            /* Info */
            data-[type=info]:bg-black
            data-[type=info]:text-white
          `,
        },
        duration: 4000,
      }}
      style={
        {
          "--normal-bg": theme === "dark" ? "#000000" : "#ffffff",
          "--normal-text": theme === "dark" ? "#ffffff" : "#000000",
          "--normal-border": theme === "dark" ? "#ffffff" : "#000000",
        } as React.CSSProperties
      }
      {...props}
    />
  );
};

export { Toaster };
