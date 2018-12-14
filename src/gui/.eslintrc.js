// http://eslint.org/docs/user-guide/configuring

const verbosity = process.env.NODE_ENV === 'production' ? 'error' : 'off'

module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    // https://github.com/vuejs/eslint-plugin-vue#priority-a-essential-error-prevention
    // consider switching to `plugin:vue/strongly-recommended` or `plugin:vue/recommended` for stricter rules.
    'plugin:vue/recommended',
    // https://github.com/standard/standard/blob/master/docs/RULES-en.md
    '@vue/standard',
    'plugin:vue-types/strongly-recommended',
    'plugin:security/recommended',
  ],
  settings: {
    'vue-types/namespace': ['VueTypes', 'AppTypes'],
  },
  // required to lint *.vue files
  plugins: [
    'vue',
    'security',
    // 'html'
  ],
  // add your custom rules here
  rules: {
    // allow paren-less arrow functions
    'arrow-parens': 0,
    // allow async-await
    'generator-star-spacing': 0,
    'comma-dangle': ['error', 'only-multiline'],
    // allow debugger during development
    'no-console': verbosity,
    'no-debugger': verbosity,
    'vue/attribute-hyphenation': ['error', 'always'],
    'vue/attributes-order': 'error',
    'vue/html-quotes': ['error', 'double'],
    'vue/component-name-in-template-casing': ['error', 'kebab-case', {
      'ignores': []
    }],
  },
  parserOptions: {
    parser: 'babel-eslint',
  },
}
