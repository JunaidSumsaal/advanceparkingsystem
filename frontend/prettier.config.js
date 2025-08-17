/** @type {import('prettier').Config} */
export default {
  plugins: ['prettier-plugin-tailwindcss'],
  tailwindAttributes: ['theme'],
  tailwindFunctions: ['twMerge', 'createTheme']
};
