# SEO & GEO Optimisation — Design Spec

**Date:** 2026-05-08
**Scope:** Meta tags + structured data + discovery files (Option B)
**Goal:** Google ranking, AI citation (GEO), and quality link previews

---

## Goals

1. **Google ranking** — surface in searches like "GDPR markdown download", "EUR-Lex converter", "EU AI Act text"
2. **AI citation (GEO)** — get cited by ChatGPT, Perplexity, Claude when users ask about EU law tools
3. **Link previews** — correct title, description, and card when shared on Slack, LinkedIn, Twitter

## Out of Scope

- Pre-rendered static pages per document (no architectural changes)
- On-page visible descriptive text section
- OG image / social card graphic

---

## Changes

### 1. `public/index.html` — `<head>` additions

**Title:**
```
EUR-Lex to Markdown Converter – Free EU Legal Document Tool
```

**Meta description:**
```
Convert EU legal documents to clean Markdown. Paste any EUR-Lex URL or CELEX ID
— get GDPR, EU AI Act, DORA, DSA, and more as structured Markdown instantly.
Free, no login required.
```

**Additional meta tags:**
```html
<meta name="robots" content="index, follow" />
<link rel="canonical" href="https://eurlex-to-md.vercel.app/" />

<!-- Open Graph -->
<meta property="og:type"        content="website" />
<meta property="og:url"         content="https://eurlex-to-md.vercel.app/" />
<meta property="og:title"       content="EUR-Lex to Markdown Converter – Free EU Legal Document Tool" />
<meta property="og:description" content="Convert EU legal documents to clean Markdown. Paste any EUR-Lex URL or CELEX ID — get GDPR, EU AI Act, DORA, DSA, and more as structured Markdown instantly. Free, no login required." />

<!-- Twitter Card -->
<meta name="twitter:card"        content="summary" />
<meta name="twitter:title"       content="EUR-Lex to Markdown Converter – Free EU Legal Document Tool" />
<meta name="twitter:description" content="Convert EU legal documents to clean Markdown. Paste any EUR-Lex URL or CELEX ID — get GDPR, EU AI Act, DORA, DSA, and more as structured Markdown instantly. Free, no login required." />
```

**JSON-LD structured data:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "EUR-Lex to Markdown Converter",
  "url": "https://eurlex-to-md.vercel.app",
  "applicationCategory": "Utilities",
  "operatingSystem": "Web",
  "description": "Converts EU legal documents from EUR-Lex into structured Markdown. Supports any CELEX ID — GDPR, EU AI Act, DMA, DSA, DORA, NIS2, and more.",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "EUR"
  },
  "about": {
    "@type": "Thing",
    "name": "EU Legislation",
    "description": "Official European Union legislation from EUR-Lex, including regulations and directives such as GDPR, the EU AI Act, the Digital Markets Act, and the Digital Services Act."
  }
}
</script>
```

---

### 2. `public/llms.txt` (new file)

For AI crawlers (ChatGPT, Perplexity, Claude). Plain text at `/llms.txt`:

```
# EUR-Lex to Markdown Converter

> Free web tool that converts EU legal documents into clean, structured Markdown.
> Input a CELEX ID or EUR-Lex URL; get back Markdown ready to read, download, or process with AI.

## Supported documents

- GDPR (32016R0679) — General Data Protection Regulation
- EU AI Act (32024R1689) — Artificial Intelligence Act
- Digital Markets Act / DMA (32022R1925)
- Digital Services Act / DSA (32022R2065)
- NIS2 Directive (32022L2555)
- EU Data Act (32023R2854)
- Cybersecurity Act (32019R0881)
- DORA (32022R2554) — Digital Operational Resilience Act

## API

GET /generate/{celex_id} — JSON with title, article_count, markdown
GET /health — cache status

## Source

Fetches from the CELLAR linked-data API (Publications Office of the EU).
Built on the eurlex library by K.M.J. Jacobs (MIT).
```

---

### 3. `public/robots.txt` (new file)

```
User-agent: *
Allow: /
Sitemap: https://eurlex-to-md.vercel.app/sitemap.xml
```

---

### 4. `public/sitemap.xml` (new file)

Single URL (SPA with one page):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://eurlex-to-md.vercel.app/</loc>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
    <lastmod>2026-05-08</lastmod>
  </url>
</urlset>
```

---

## Canonical URL Note

All files use `https://eurlex-to-md.vercel.app` as the base URL. If the actual deployed Vercel URL differs, do a find-and-replace across all four files before deploying.

---

## Files Changed

| File | Change |
|---|---|
| `public/index.html` | Add meta tags + JSON-LD to `<head>` |
| `public/llms.txt` | New — AI crawler discovery |
| `public/robots.txt` | New — crawler permissions + sitemap pointer |
| `public/sitemap.xml` | New — single-URL sitemap |
