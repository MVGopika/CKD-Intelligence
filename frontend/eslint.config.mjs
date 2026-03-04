import { FlatCompat } from "@eslint/eslintrc";

const compat = new FlatCompat();

export default [
  ...compat.config({
    extends: "next/core-web-vitals",
  }),
  {
    rules: {
      "@next/next/no-html-link-for-pages": "off",
    },
  },
];
