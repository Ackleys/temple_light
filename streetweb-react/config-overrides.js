const { 
  override,
  overrideDevServer,
  disableEsLint,
  addLessLoader,
  addWebpackAlias,
  addBabelPlugin,
  fixBabelImports,
} = require('customize-cra');
const path =require('path');
const rewireReactHotLoader = require('react-app-rewire-hot-loader');

module.exports = {
  webpack: override(
    disableEsLint(),
    addLessLoader({
      lessOptions: {
        // modifyVars: { '@primary-color': '#1DA57A' },
        javascriptEnabled: true,
      }
    }),
    fixBabelImports('import', {
      libraryName: 'antd',
      libraryDirectory: 'es',
      style: 'css',
    }),
    addBabelPlugin('react-hot-loader/babel'),
    addWebpackAlias({
      '@pages$': path.resolve(__dirname, './src/pages/admin'),
      '@pages/common': path.resolve(__dirname, './src/pages/admin/common'),
      '@pages': path.resolve(__dirname, './src/pages/admin/streetweb'),
      'react-dom': process.env.NODE_ENV === 'production' ? 'react-dom' : '@hot-loader/react-dom'
    }),
  ),
  devServer: overrideDevServer(
    conf => ({
      ...conf,
      proxy: {
        '/admin': {
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
