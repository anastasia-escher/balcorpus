# Balcorpus website

The Nuxt site of the corpus. It is a static single-page app: the build is a
folder of plain files that talk to the API under `/api/v1/`.

Always use **yarn**, never npm or pnpm. `yarn.lock` holds the exact versions
that were tested, and only yarn reads it; `--frozen-lockfile` stops with an
error instead of quietly installing different versions.

## Development

Normally run through Docker from the project root (see the main README). On
its own:

```bash
yarn install --frozen-lockfile
yarn dev
```

## Tests

```bash
yarn test
yarn typecheck
```

## Production build

```bash
yarn install --frozen-lockfile
NUXT_PUBLIC_API_BASE_URL= yarn build
```

The result is in `.output/public/`. How it gets to the server is described in
`php/ЗАГРУЗКА.md`. The empty `NUXT_PUBLIC_API_BASE_URL` makes the site ask
the same domain it was loaded from.
