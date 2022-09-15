const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,

  pluginOptions: {
    vuetify: {
			// https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
		}
  },
  devServer: {
    proxy: {
      '^/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        },
        logLevel: 'debug',
      },
      '^/subscribe': {
        target: 'http://localhost:8000/subscribe',
        ws: true,
        pathRewrite: {
          '^/subscribe': '/subscribe'
        },
        changeOrigin: true,
        logLevel: 'debug'
    }
    }
  }
})
