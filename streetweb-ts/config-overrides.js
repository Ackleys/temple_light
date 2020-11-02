const { 
  override,
  overrideDevServer,
  disableEsLint,
  addLessLoader,
  addWebpackAlias,
  addBabelPlugin,
  fixBabelImports,
  adjustStyleLoaders,
} = require('customize-cra');
const path =require('path');

module.exports = {
  webpack: override(
    disableEsLint(),
    addLessLoader({
      lessOptions: {
        // modifyVars: { '@primary-color': '#1DA57A' },
        javascriptEnabled: true,
      },
    }),
    adjustStyleLoaders(({use: [, {options: css}]}) => {
      css.localsConvention = 'camelCase';
    }),
    fixBabelImports('import', {
      libraryName: 'antd',
      libraryDirectory: 'es',
      style: 'css',
    }),
    addBabelPlugin('react-hot-loader/babel'),
    addWebpackAlias({
      '@pages$': path.resolve(__dirname, './src/pages/admin'),
      '@common': path.resolve(__dirname, './src/pages/admin/common'),
      '@pages': path.resolve(__dirname, './src/pages/admin/streetweb'),
      'react-dom': process.env.NODE_ENV === 'production' ? 'react-dom' : '@hot-loader/react-dom',
      '@api': path.resolve(__dirname, './src/api'),
    }),
  ),
  devServer: overrideDevServer(
    conf => ({
      ...conf,
      proxy: {
        '/admin/': {
          target: 'http://server.fzstack.com',
          changeOrigin: true,
        },
        '/static': {
          target: 'http://server.fzstack.com',
          changeOrigin: true,
        },
      },
    }),
  ),
};
