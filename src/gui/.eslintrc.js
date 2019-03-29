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
    'plugin:security/recommended',
    'plugin:vue/recommended',
    'plugin:vue-types/strongly-recommended',
    '@vue/typescript',
    'plugin:@typescript-eslint/recommended',
  ],

  settings: {
    'vue-types/namespace': ['VueTypes', 'AppTypes'],
    'import/resolver': {
      node: {
        extensions: ['.js', '.ts'],
      }
    },
  },

  // required to lint *.vue files
  plugins: [
    'vue',
    'security',
    // 'html'
    '@typescript-eslint',
  ],

  // add your custom rules here
  rules: {
    'operator-linebreak': ['error', 'before'],
    '@typescript-eslint/indent': ['error', 2],
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
      ignores: []
    }],
  },
  overrides: [
    {
      files: ['*.js'],
      rules: {
        '@typescript-eslint/no-use-before-define': ['error', { functions: false, classes: false, variables: false }],
        '@typescript-eslint/no-var-requires': 'off',
      },
    },
    {
      files: ['*.ts', '*.vue'],
      rules: {
        'no-useless-constructor': 1 /* warning */,
        '@typescript-eslint/member-delimiter-style': ['error', {
          multiline: {
            delimiter: 'none'
          },
          singleline: {
            delimiter: 'comma'
          },
        }],
      },
      parserOptions: {
        parser: '@typescript-eslint/parser',
      }
    },
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 2017,
    sourceType: 'module',
    ecmaFeatures: { // See https://github.com/babel/babel-eslint/issues/662
      legacyDecorators: true,
    },
  },
}
