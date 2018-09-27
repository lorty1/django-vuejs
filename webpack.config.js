var path = require('path');
var webpack = require('./node_modules/webpack');
var BundleTracker = require('./node_modules/webpack-bundle-tracker');

module.exports = {
	    context: __dirname,
	    entry: './lessimonettes/apps/vuejs/assets/js/index.js',
	    output: {
		            path: path.resolve('./lessimonettes/apps/vuejs/assets/bundles/'),
		            filename: 'app.js'
		        },

	    plugins: [
		            new BundleTracker({filename: './webpack-stats.json'}),
		        ],

	    module: {
		            rules: [
				                {
							                test: /\.js$/,
							                exclude: /node_modules/,
							                loader: 'babel-loader',
							            },
				                {
							                test: /\.vue$/,
							                loader: 'vue-loader',

							            },
				                {
							                test: /\.css$/,
							                use: [ 'style-loader', 'css-loader' ]
							            }
				            ],
		        },
	    resolve: {
		            alias: {vue: 'vue/dist/vue.js'}
		        },

};
