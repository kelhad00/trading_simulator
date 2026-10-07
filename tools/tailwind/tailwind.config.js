// Builds trade/assets/tailwind.css: only the Tailwind classes the app uses,
// so the app works without internet. Rebuild after adding new classes: see README.
module.exports = {
  content: ["./trade/**/*.py", "!./trade/venv/**", "!./trade/**/__pycache__/**"],
  theme: { extend: {} },
  plugins: [],
};
