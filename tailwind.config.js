/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/src/**/*.js",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        uiablue: "#191A39",
        uiared: "#C8102E",
        uiagray: "##F8EDDD",
      }
    },
  },
  plugins: [
    require("flowbite/plugin")
  ],
}
