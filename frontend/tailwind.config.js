/** @type {import('tailwindcss').Config} */
import { join } from 'path';
import { skeleton } from '@skeletonlabs/tw-plugin';

export default {
	darkMode: 'class',
	content: [
		'./src/**/*.{html,js,svelte,ts}',
		join(require.resolve('@skeletonlabs/skeleton'), '../**/*.{html,js,svelte,ts}')
	],
	theme: {
		extend: {},
	},
	plugins: [
		skeleton({
			themes: {
				preset: [
					{
						name: 'skeleton',
						enhancements: true,
					},
					{
						name: 'wintry',
						enhancements: true,
					},
					{
						name: 'modern',
						enhancements: true,
					},
					{
						name: 'rocket',
						enhancements: true,
					},
					{
						name: 'seafoam',
						enhancements: true,
					},
					{
						name: 'vintage',
						enhancements: true,
					},
					{
						name: 'sahara',
						enhancements: true,
					},
					{
						name: 'hamlindigo',
						enhancements: true,
					},
					{
						name: 'gold-nouveau',
						enhancements: true,
					},
					{
						name: 'crimson',
						enhancements: true,
					},
				],
				custom: [
					{
						name: 'universal-agents',
						properties: {
							// =~= Theme Properties =~=
							"--theme-font-family-base": `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'`,
							"--theme-font-family-heading": `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'`,
							"--theme-font-color-base": "0 0 0",
							"--theme-font-color-dark": "255 255 255",
							"--theme-rounded-base": "2px",
							"--theme-rounded-container": "2px",
							"--theme-border-base": "2px",
							// =~= Theme On-X Colors =~=
							"--on-primary": "0 0 0",
							"--on-secondary": "0 0 0",
							"--on-tertiary": "0 0 0",
							"--on-success": "0 0 0",
							"--on-warning": "0 0 0",
							"--on-error": "255 255 255",
							"--on-surface": "255 255 255",
							// =~= Theme Colors  =~=
							// primary | #3fff8c 
							"--color-primary-50": "226 255 238", // #e2ffee
							"--color-primary-100": "217 255 232", // #d9ffe8
							"--color-primary-200": "207 255 226", // #cfffe2
							"--color-primary-300": "178 255 209", // #b2ffd1
							"--color-primary-400": "121 255 175", // #79ffaf
							"--color-primary-500": "63 255 140", // #3fff8c
							"--color-primary-600": "57 230 126", // #39e67e
							"--color-primary-700": "47 191 105", // #2fbf69
							"--color-primary-800": "38 153 84", // #269954
							"--color-primary-900": "31 125 69", // #1f7d45
							// secondary | #ED72B7 
							"--color-secondary-50": "252 234 244", // #fceaf4
							"--color-secondary-100": "251 227 241", // #fbe3f1
							"--color-secondary-200": "251 220 237", // #fbdced
							"--color-secondary-300": "248 199 226", // #f8c7e2
							"--color-secondary-400": "242 156 205", // #f29ccd
							"--color-secondary-500": "237 114 183", // #ED72B7
							"--color-secondary-600": "213 103 165", // #d567a5
							"--color-secondary-700": "178 86 137", // #b25689
							"--color-secondary-800": "142 68 110", // #8e446e
							"--color-secondary-900": "116 56 90", // #74385a
							// tertiary | #25b1ff 
							"--color-tertiary-50": "222 243 255", // #def3ff
							"--color-tertiary-100": "211 239 255", // #d3efff
							"--color-tertiary-200": "201 236 255", // #c9ecff
							"--color-tertiary-300": "168 224 255", // #a8e0ff
							"--color-tertiary-400": "102 200 255", // #66c8ff
							"--color-tertiary-500": "37 177 255", // #25b1ff
							"--color-tertiary-600": "33 159 230", // #219fe6
							"--color-tertiary-700": "28 133 191", // #1c85bf
							"--color-tertiary-800": "22 106 153", // #166a99
							"--color-tertiary-900": "18 87 125", // #12577d
							// success | #84cc16 
							"--color-success-50": "237 247 220", // #edf7dc
							"--color-success-100": "230 245 208", // #e6f5d0
							"--color-success-200": "224 242 197", // #e0f2c5
							"--color-success-300": "206 235 162", // #ceeba2
							"--color-success-400": "169 219 92", // #a9db5c
							"--color-success-500": "132 204 22", // #84cc16
							"--color-success-600": "119 184 20", // #77b814
							"--color-success-700": "99 153 17", // #639911
							"--color-success-800": "79 122 13", // #4f7a0d
							"--color-success-900": "65 100 11", // #41640b
							// warning | #EAB308 
							"--color-warning-50": "252 244 218", // #fcf4da
							"--color-warning-100": "251 240 206", // #fbf0ce
							"--color-warning-200": "250 236 193", // #faecc1
							"--color-warning-300": "247 225 156", // #f7e19c
							"--color-warning-400": "240 202 82", // #f0ca52
							"--color-warning-500": "234 179 8", // #EAB308
							"--color-warning-600": "211 161 7", // #d3a107
							"--color-warning-700": "176 134 6", // #b08606
							"--color-warning-800": "140 107 5", // #8c6b05
							"--color-warning-900": "115 88 4", // #735804
							// error | #D41976 
							"--color-error-50": "249 221 234", // #f9ddea
							"--color-error-100": "246 209 228", // #f6d1e4
							"--color-error-200": "244 198 221", // #f4c6dd
							"--color-error-300": "238 163 200", // #eea3c8
							"--color-error-400": "225 94 159", // #e15e9f
							"--color-error-500": "212 25 118", // #D41976
							"--color-error-600": "191 23 106", // #bf176a
							"--color-error-700": "159 19 89", // #9f1359
							"--color-error-800": "127 15 71", // #7f0f47
							"--color-error-900": "104 12 58", // #680c3a
							// surface | #222222 
							"--color-surface-50": "222 222 222", // #dedede
							"--color-surface-100": "211 211 211", // #d3d3d3
							"--color-surface-200": "200 200 200", // #c8c8c8
							"--color-surface-300": "167 167 167", // #a7a7a7
							"--color-surface-400": "100 100 100", // #646464
							"--color-surface-500": "34 34 34", // #222222
							"--color-surface-600": "31 31 31", // #1f1f1f
							"--color-surface-700": "26 26 26", // #1a1a1a
							"--color-surface-800": "20 20 20", // #141414
							"--color-surface-900": "17 17 17", // #111111
							
							// Background image
							"--theme-bg-image": "radial-gradient(at 0% 0%, rgba(var(--color-primary-500) / 0.33) 0px, transparent 50%), radial-gradient(at 98% 1%, rgba(var(--color-tertiary-500) / 0.33) 0px, transparent 50%)",
							"--theme-bg-attachment": "fixed",
							"--theme-bg-position": "center",
							"--theme-bg-repeat": "no-repeat",
							"--theme-bg-size": "cover"
						},
						properties_dark: {},
						enhancements: true
					}
				]
			},
			defaultTheme: 'universal-agents',
		}),
	],
}