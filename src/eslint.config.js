// ESLint configuration for BlockList project
// https://eslint.org/docs/latest/use/configure/

export default [
  {
    files: ["static/deepweb/js/**/*.js"],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "script",
      globals: {
        // Browser globals
        window: "readonly",
        document: "readonly",
        console: "readonly",
        fetch: "readonly",
        URL: "readonly",
        setTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",

        // Libraries
        Chart: "readonly",
        bootstrap: "readonly",
      },
    },
    rules: {
      // Possible errors
      "no-console": "off", // Allow console for debugging
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "no-undef": "error",

      // Best practices
      "eqeqeq": ["error", "always"], // Require === and !==
      "no-var": "warn", // Prefer let/const over var
      "prefer-const": "warn",

      // Null safety (prevents bugs like the one we had)
      "no-unsafe-optional-chaining": "error",
      "no-constant-binary-expression": "error",

      // Code quality
      "no-empty": "warn",
      "no-unreachable": "error",
      "no-duplicate-case": "error",

      // Style (optional, can be disabled)
      "semi": ["warn", "always"],
      "quotes": ["warn", "single", { avoidEscape: true }],
      // Indent disabled - too strict for mixed HTML/JS templates
      // "indent": ["warn", 2],
    },
  },
];
