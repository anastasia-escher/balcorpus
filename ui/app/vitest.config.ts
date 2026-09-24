import {dirname} from 'node:path'
import {fileURLToPath} from 'node:url'
import {defineConfig} from 'vitest/config'

// Tests are run by vitest alone, without Nuxt, so the '~' of an import has to
// be spelled out here; Nuxt's own configuration is not read.
const appDirectory = dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  resolve: {
    alias: [{find: '~', replacement: appDirectory}],
  },
})
