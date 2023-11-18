/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [],
  purge: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        text: "#f6daef",
        background: "#060C03",
        primary: "#FF3B5C",
        hover: "#ED2345",
        secondary: "#471d10",
        accent: "#d56f4d",
      },
    },
  },
  plugins: [],
};
