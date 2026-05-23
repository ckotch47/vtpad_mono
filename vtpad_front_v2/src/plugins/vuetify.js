/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import {createVuetify } from 'vuetify'
import {md3} from "vuetify/blueprints";
import { VTreeview } from 'vuetify/labs/VTreeview'

let theme = 'light'
const userTheme = localStorage.getItem('useTheme')
if(!userTheme)
  localStorage.setItem('useTheme', 'system')
if(window.matchMedia('(prefers-color-scheme: dark)').matches){
  theme = 'dark'
}
if(userTheme && userTheme !== 'system')
  theme = userTheme

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  blueprint: md3,
  components: { VTreeview },
  styles: {
    configFile: 'src/styles/settings.scss',
  },
  theme: {
    themes: {
      light:{
        colors: {
          primary: '#26a69a',

        }
      },
      dark:{
        colors: {
          primary: '#26a69a',

        }
      }
    },

    defaultTheme: theme,
  },
})

