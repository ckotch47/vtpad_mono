import { Extension } from '@tiptap/core'
import Suggestion from '@tiptap/suggestion'
import tippy from 'tippy.js'
import { VueRenderer } from '@tiptap/vue-3'
import SlashMenu from './editorSlashMenu.vue'

const slashItems = [
  {
    title: 'Heading 2',
    description: 'Large section heading',
    icon: 'mdi-format-header-2',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setNode('heading', { level: 2 }).run()
    }
  },
  {
    title: 'Heading 3',
    description: 'Medium section heading',
    icon: 'mdi-format-header-3',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setNode('heading', { level: 3 }).run()
    }
  },
  {
    title: 'Bullet List',
    description: 'Simple bullet list',
    icon: 'mdi-format-list-bulleted',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleBulletList().run()
    }
  },
  {
    title: 'Ordered List',
    description: 'Numbered list',
    icon: 'mdi-order-numeric-ascending',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleOrderedList().run()
    }
  },
  {
    title: 'Task List',
    description: 'List with checkboxes',
    icon: 'mdi-format-list-checkbox',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleTaskList().run()
    }
  },
  {
    title: 'Code Block',
    description: 'Block of highlighted code',
    icon: 'mdi-code-braces',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleCodeBlock().run()
    }
  },
  {
    title: 'Blockquote',
    description: 'Quote block',
    icon: 'mdi-format-quote-close',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleBlockquote().run()
    }
  },
  {
    title: 'Table',
    description: '3×3 table with header',
    icon: 'mdi-table',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
    }
  },
  {
    title: 'Horizontal Rule',
    description: 'Divider line',
    icon: 'mdi-minus',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setHorizontalRule().run()
    }
  }
]

function filterSlashItems(query) {
  const q = query.toLowerCase()
  return slashItems
    .filter(i => i.title.toLowerCase().includes(q) || i.description.toLowerCase().includes(q))
    .slice(0, 10)
}

export default Extension.create({
  name: 'slashCommands',

  addOptions() {
    return {
      suggestion: {
        char: '/',
        command: ({ editor, range, props }) => {
          props.command({ editor, range })
        },
        items: ({ query }) => filterSlashItems(query),
        render: () => {
          let component
          let popup

          return {
            onStart: props => {
              component = new VueRenderer(SlashMenu, {
                editor: props.editor,
                props: {
                  items: props.items,
                  command: props.command
                }
              })

              if (!props.clientRect) {
                return
              }

              popup = tippy('body', {
                getReferenceClientRect: props.clientRect,
                appendTo: () => document.body,
                content: component.element,
                showOnCreate: true,
                interactive: true,
                trigger: 'manual',
                placement: 'bottom-start'
              })
            },

            onUpdate(props) {
              component.updateProps({
                items: props.items,
                command: props.command
              })

              if (popup && popup[0]) {
                popup[0].setProps({
                  getReferenceClientRect: props.clientRect
                })
              }
            },

            onKeyDown(props) {
              if (props.event.key === 'Escape') {
                if (popup && popup[0]) {
                  popup[0].hide()
                }
                return true
              }
              return component.ref?.onKeyDown(props)
            },

            onExit() {
              if (popup && popup[0]) {
                popup[0].destroy()
              }
              component.destroy()
            }
          }
        }
      }
    }
  },

  addProseMirrorPlugins() {
    return [
      Suggestion({
        editor: this.editor,
        ...this.options.suggestion
      })
    ]
  }
})
