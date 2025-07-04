const {
  defineConfigWithVueTs,
  vueTsConfigs,
} = require('@vue/eslint-config-typescript')
const vue = require('eslint-plugin-vue')
const vuetify = require('eslint-plugin-vuetify')
const security = require('eslint-plugin-security')
const stylisticTs = require('@stylistic/eslint-plugin')
const globals = require('globals')
const parser = require('vue-eslint-parser')
const js = require('@eslint/js')
const skipFormatting = require('@vue/eslint-config-prettier/skip-formatting')

const verbosity = process.env.NODE_ENV === 'production' ? 'error' : 'off'

module.exports = defineConfigWithVueTs(
  js.configs.recommended,

  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  {
    name: 'app/files-to-ignore',
    ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**'],
  },
  vue.configs['flat/recommended'],
  vueTsConfigs.recommended,
  // There is a problem using vuetify's config together with vue's;
  // vuetify tries to overwrite the `vue` plugin provided by `vue.configs['flat/recommended']`
  {
    plugins: {
      vuetify,
    },
  },
  ...vuetify.configs['flat/recommended'].map(({ rules }) => ({
    rules,
  })),
  security.configs.recommended,

  {
    plugins: {
      '@stylistic/ts': stylisticTs,
    },
  },
  {
    languageOptions: {
      globals: { ...globals.browser },
      parser: parser,
      ecmaVersion: 2020,
      sourceType: 'module',
      parserOptions: {
        parser: '@typescript-eslint/parser',
      },
    },
  },
  {
    settings: {
      'import/resolver': {
        node: {
          extensions: ['.js', '.ts'],
        },
      },
    },
  },
  // add your custom rules here
  {
    rules: {
      // There is [an issue](https://github.com/vuejs/eslint-plugin-vue/issues/1000), that causes the @Component
      // to complain that the _keys_ on an object is not defined.
      // Once resolved, no-undef can be turned on again.
      'no-undef': 'off',
      indent: 'off',
      'operator-linebreak': ['error', 'before'],
      '@stylistic/ts/indent': ['error', 2],
      // allow paren-less arrow functions
      'arrow-parens': 0,
      // allow async-await
      'generator-star-spacing': 0,
      'comma-dangle': ['error', 'only-multiline'],
      // allow debugger during development
      'no-console': verbosity,
      'no-debugger': verbosity,
      // We have multiple components with a single word, but ...
      'vue/multi-word-component-names': 'off',
      'vue/attribute-hyphenation': ['error', 'always'],
      'vue/attributes-order': 'error',
      'vue/html-quotes': ['error', 'double'],
      'vue/component-name-in-template-casing': [
        'error',
        'kebab-case',
        {
          ignores: [],
        },
      ],
      'vue/no-mutating-props': [
        'error',
        {
          shallowOnly: true,
        },
      ],
      'vuetify/no-deprecated-classes': 'error',
      // To be added when the documentation for v-col / v-row has been improved (made available)
      'vuetify/grid-unknown-attributes': 'error',
      // 'vuetify/no-legacy-grid': 'error',
      '@typescript-eslint/naming-convention': [
        'error',
        {
          selector: 'variableLike',
          format: ['camelCase', 'PascalCase', 'UPPER_CASE'],
          leadingUnderscore: 'allow',
        },
        {
          selector: 'memberLike',
          format: ['camelCase', 'PascalCase', 'UPPER_CASE'],
          leadingUnderscore: 'allow',
        },
      ],
      // This rules is not relly relevant for us
      'security/detect-object-injection': 'off',
    },
  },
  {
    files: ['**/*.js'],
    rules: {
      '@typescript-eslint/no-use-before-define': [
        'error',
        { functions: false, classes: false, variables: false },
      ],
      '@typescript-eslint/no-var-requires': 'off',
    },
  },
  {
    files: ['*.ts', '*.vue'],
    rules: {
      'no-useless-constructor': 1 /* warning */,
      '@stylistic/ts/member-delimiter-style': [
        'error',
        {
          multiline: {
            delimiter: 'none',
          },
          singleline: {
            delimiter: 'comma',
          },
        },
      ],
    },
  },
  skipFormatting,
  {
    files: ['**/*.cjs'],
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
    },
  },
)
