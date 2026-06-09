import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}", "./lib/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        lucro: {
          50: "#f0fdf4",
          600: "#16a34a",
          700: "#15803d",
          950: "#052e16"
        }
      }
    }
  },
  plugins: []
};

export default config;
