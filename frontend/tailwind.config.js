/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        maku: { 50: "#f3f1fa", 100: "#e4dff4", 500: "#4b3a9c", 600: "#3d2e85", 700: "#2f2368" },
      },
    },
  },
  plugins: [],
};
