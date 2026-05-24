# VTPad Frontend Guide

## Tech Stack

| Concern | Technology |
|---------|------------|
| Framework | Vue 3.4 |
| UI Library | Vuetify 3 |
| Build Tool | Vite 5.1 |
| Routing | unplugin-vue-router (file-based) |
| Layouts | vite-plugin-vue-layouts |
| State | Pinia |
| HTTP | Axios |
| Editor | TipTap v2 |
| Charts | Chart.js / vue-chartjs |
| Toasts | vue3-toastify |

## Routing

Routes are auto-generated from files in `src/pages/`.

### Dynamic Segments
- `space/:spaceId/` → colon prefix for dynamic folders
- `[caseId]/index.vue` → bracket notation for dynamic files

### Route Meta
Define layout and tab via `<route>` block:
```vue
<route>
{
  meta: {
    layout: "spaces",
    tabValue: "test-suites"
  }
}
</route>
```

### Layouts
- `default.vue` — auth, profile, 404
- `spaces.vue` — space-scoped pages (has top tab bar)
- `spacesReport.vue` — report pages
- `spacesSettings.vue` — settings pages
- `company.vue` — company admin

### Important: Dev Server Restart
**unplugin-vue-router requires `npm run dev` restart when adding new pages.**

## Component Conventions

### Naming
- PascalCase for components: `testCasesListComponent.vue`
- Group by domain: `test-suites/`, `test-cases/`, `bugs/`

### API Calls
Import axios directly:
```js
import axios from "axios";
axios.get(`/api/v2/test-case/${this.caseId}`)
```

### Options API vs Composition API
Both are used. Newer pages tend toward `<script setup>`, older use Options API.

### Editor Component
Reusable TipTap wrapper:
```vue
<editor-component
  :text="content"
  :edit="true|false"
  :show-menu-fixed="true"
  @editor-update="content = $event"
/>
```

## State Management

Minimal Pinia store in `src/stores/app.js`:
```js
export const useAppStore = defineStore('app', {
  state: () => ({
    openBug: undefined,
    openSpaceId: undefined,
  })
})
```

All list/pagination/filter state lives locally in components.

## Adding a New Feature

1. **Backend first**: Create model, DTO, service, router in `vtpad_backend/app/src/`
2. **Register router**: Add to `app/main.py`
3. **Migration**: Add JSON migration in `app/src/migration/data/`
4. **Frontend page**: Create `.vue` under `src/pages/space/:spaceId/...`
5. **Component**: Create component in `src/components/`
6. **Layout tab**: If needed, add tab to `src/layouts/spaces.vue`
7. **Restart dev server**: `npm run dev`

## Key Components

| Component | Purpose |
|-----------|---------|
| `editorComponent.vue` | TipTap rich text editor |
| `breadcrumbsComponent.vue` | Navigation breadcrumbs |
| `commandPaletteComponent.vue` | Cmd+K search modal |
| `testSuitesListComponent.vue` | Suite table with CRUD |
| `testSuiteDetailComponent.vue` | Suite tree + cases |
| `testCasesListComponent.vue` | Case table with filters |
| `testCaseDetailComponent.vue` | Case view + run history |
| `testRunsListComponent.vue` | Run table |
| `testRunDetailComponent.vue` | Run execution UI |
| `testPlansListComponent.vue` | Plan table |
| `testPlanDetailComponent.vue` | Plan view + create run |
| `dashboardComponent.vue` | Space analytics dashboard |
| `tech-docs/index.vue` | Wiki tree + editor |

## Environment Variables

```
VITE_API_BASE_URL=http://localhost:8000
```
