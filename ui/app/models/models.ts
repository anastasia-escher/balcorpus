// models.ts

// ------------------------------------------------------------------
// 0. Brief (“shallow”) interfaces to avoid deep nesting
// ------------------------------------------------------------------

export interface SourceBrief {
  id: number
  name: string
}

export interface LocationBrief {
  id: number
  name: string | null
}

export interface LanguageBrief {
  id: number
  name: string
  russian_name: string | null
}

export interface DialectBrief {
  id: number
  name: string
  russian_name: string | null
}

export interface IdiomBrief {
  id: number
  name: string
  russian_name: string | null
}

export interface CategoryBrief {
  id: number
  name: string
  russian_name: string | null
}

export interface ValueBrief {
  id: number
  name: string
  russian_name: string | null
}

export interface FeatureBrief {
  id: number
  name: string
  russian_name: string | null
}

export interface ExampleBrief {
  id: number
  name: string
}
export interface ValueBrief {
  name: string
  russian_name: string | null
  description: string | null
  russian_description: string | null
}

// ------------------------------------------------------------------
// 1. Token & Analysis (leaf‐level models)
// ------------------------------------------------------------------

export interface Token {
  id: number
  order: number
  text: string
  morphemes_text: string | null
  lemma: string | null
  gloss: string | null
  russian_translation: string | null
  english_translation: string | null
  token_type: 'word' | 'punctuation' | 'number' | 'symbol' | 'other'
  example: ExampleBrief
}

export interface Analysis {
  id: number
  name: string
  russian_name: string | null
  text: string
  example: ExampleBrief
  author: string | null // serialized as StringRelatedField, so likely username or null
}

// ------------------------------------------------------------------
// 2. Category, Value & Feature
// ------------------------------------------------------------------

export interface Feature {
  id: number
  name: string
  russian_name: string | null
  description: string | null
  russian_description: string | null
  category: CategoryBrief | null
  language: LanguageBrief | null
  dialect: DialectBrief | null
  idiom: IdiomBrief | null
  value: ValueBrief | null
  examples: ExampleBrief[]
  sources: Source[]
  languages: LanguageBrief[]
  dialects: DialectBrief[]
  idioms: IdiomBrief[]
  locations: LocationBrief[]
  values: ValueBrief[]
  number_of_examples: number
  base_language: number | null
}

export interface Category {
  id: number
  name: string
  russian_name: string | null
  description: string | null
  russian_description: string | null
  features: Feature[]
  examples: ExampleBrief[]
  sources: Source[]
  base_language: LanguageBrief | null
  number_of_examples: number
}

// ------------------------------------------------------------------
// 3. Language Hierarchy: Language → Dialect → Idiom
// ------------------------------------------------------------------

export interface Idiom {
  id: number
  name: string
  english_name: string | null
  russian_name: string | null
  language: LanguageBrief | null
  dialect: DialectBrief | null
  description: string | null
  russian_description: string | null
  location: LocationBrief | null
  features: Feature[]
  examples: ExampleBrief[]
}

export interface Dialect {
  id: number
  name: string
  english_name: string | null
  russian_name: string | null
  language: LanguageBrief
  description: string | null
  russian_description: string | null
  location: LocationBrief | null
  idioms: Idiom[]
  features: Feature[]
  examples: ExampleBrief[]
}

export interface Language {
  id: number
  name: string
  english_name: string | null
  russian_name: string | null
  iso_code: string | null
  description: string | null
  russian_description: string | null
  location: LocationBrief | null
  dialects: Dialect[]
  idioms: Idiom[]
  features: Feature[]
  examples: ExampleBrief[]
  base_language: LanguageBrief | null
}

// ------------------------------------------------------------------
// 4. Source & Location
// ------------------------------------------------------------------

export interface Source {
  id: number
  name: string
  russian_name: string | null
  url: string | null
  description: string | null
  russian_description: string | null
  bibliographic_reference: string | null
  source_type:
    | 'book'
    | 'article'
    | 'dictionary'
    | 'website'
    | 'database'
    | 'manuscript'
    | 'naturalistic'
    | 'elicited'
    | 'constructed'
    | 'unknown'
    | 'other'
  examples: ExampleBrief[]
  number_of_examples: number
  categories: CategoryBrief[]
  languages: LanguageBrief[]
  dialects: DialectBrief[]
  idioms: IdiomBrief[]

  locations: LocationBrief[]
  features: FeatureBrief[]
}

export interface Location {
  id: number
  name: string | null
  english_name: string | null
  russian_name: string | null
  latitude: number | null
  longitude: number | null
  languages: LanguageBrief[]
  dialects: DialectBrief[]
  idioms: IdiomBrief[]
  examples: ExampleBrief[]
  description: string | null
  russian_description: string | null
  sources: Source[]
}

// ------------------------------------------------------------------
// 5. Example (central entity)
// ------------------------------------------------------------------

export interface Example {
  id: number
  name: string
  russian_name: string | null
  source: Source | null
  created_at: string // ISO datetime string
  original_text: string | null
  language: LanguageBrief | null
  dialect: DialectBrief | null
  idiom: IdiomBrief | null
  categories: CategoryBrief[]
  features: FeatureBrief[]
  values: ValueBrief[]
  location: LocationBrief | null
  notes: string | null
  russian_notes: string | null
  full_text: string | null
  page_source: string | null
  tokens: Token[]
  analyses: Analysis[]
  value: ValueBrief | null
  parallel_examples?: number[] | Example[]
  russian_translation: string | null
  english_translation: string | null
}

export interface Global {
  first_page_title: string | null
  first_page_russian_title: string | null
  first_page_text: string | null
  first_page_russian_text: string | null
}
