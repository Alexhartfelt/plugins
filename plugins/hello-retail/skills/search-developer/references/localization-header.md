# Localization header — translate the single-locale header in place

This is overlay chrome (the search UI's own labels: "Sort by", "Filters", result subtitle, etc.) — **not** tile content. The tile skill never touches it.

> **Source of truth for translations: `${CLAUDE_PLUGIN_ROOT}/docs/wiki/translations/translations.json` (Malin / QA).** Before translating any UI string — whether a header token here, a sale/sold-out label, or any visible copy — look the English token up in that file (`SEARCH` section for Search templates) and **use its translation for the target locale verbatim**. Only fall back to your own knowledge when the file has no entry for that token/locale, and make sure the result reads naturally for the locale. Many cells offer multiple `/`-separated options that differ by **register** (formal vs informal — DE Sie/Du, NL u/je, FR vous/tu, ES usted/tú) and sometimes quality: decide the site's register **once** from the storefront and apply it to every pick, match the customer's own wording if they already use one, prefer the natural/concise phrasing over awkward literal ones, default to formal + first option when there's no signal, and ask the operator if the formal/informal call is ambiguous and affects the whole UI. The locale tables here are convenience aids; `translations.json` wins when it covers the string. See `${CLAUDE_PLUGIN_ROOT}/docs/wiki/translations/README.md`.

## What the header looks like now

The design you read with `search_getDesign` is your modify-in-place base, and its header is **flat — one declaration per token, no `__<Language>` variants.** Each translatable string appears once, in the base language (usually English). Your job is to **rewrite each `{# text … #}` value in place** into the customer's locale. There are no variant lines to choose between or delete.

```liquid
{# text text_sorting_title = "Sort by" #}
{# text text_go_directly_to = "Go to: " #}
{# text text_product_title = "Products" #}
{# text text_filters_selected_clear_button = "Clear all filters" #}
{# text text_products = "products." #}
{# text text_category_no_content_before = "No" #}
{# text text_category_no_content_after = "were found." #}
{# boolean product_sale_label = true #}
{# color button_icon_colors = "#232324" #}
{# boolean show_product_description = false #}
{# text result_subtitle = "The search <strong> \"$query$\"</strong> matches <strong>$totalResults$</strong> $contentType$" #}
{# text text_synonym_only_suggested = "We didn't find exactly what you were looking for, but here are some products you might find interesting:" #}
{# text text_synonym_mixed = "We have expanded the search with more products that you might find interesting." #}
{# text label_filters = "Filters" #}
{# text label_clear_filter = "Clear filter" #}
{# text label_skip_to_products = "Skip to products" #}
{# text label_skip_to_input = "Skip to search input" #}
{# text label_close_search = "Close search" #}
```

The customer's final header keeps the **same keys in the same order**; only the **string values of `{# text … #}` tokens** change to the target locale.

## What you translate — and what you leave alone

- **Translate:** every `{# text … #}` whose value is user-facing copy. Rewrite the value into the target locale.
- **Leave as-is:** `{# boolean … #}`, `{# color … #}`, `{# number … #}`, `{# section … #}` — these are configuration, not copy.
- **Branding exceptions:** `webshop_name`, `header_logo_url`, and the theme color tokens are **always set to the customer's real values** regardless of locale — that's owned by `branding-and-header.md`, not translated here. (`webshop_name` happens to be a `{# text … #}` token, but you set it from branding, you don't translate "My shop".)

## Resolution algorithm (per token)

1. The locale is already resolved (operator-supplied, or inferred from `<html lang>` / `<meta http-equiv="content-language">` / TLD, confirmed via `website_getInfo`).
2. For each `{# text key = "value" #}` that is user-facing copy:
   - Look the key up in `translations.json` (`SEARCH` section) for the target locale → use that value verbatim.
   - No entry there → translate the value yourself, following the conventions below.
   - Emit the line with the same key, the translated value.
3. **If the locale IS English** (`en`, `en-GB`, `en-US`): leave the `{# text … #}` values as the English base — no translation needed. Still set branding tokens.
4. Preserve key order and the blank lines between groups so the header stays readable.
5. Preserve every non-`text` declaration unchanged (except branding).

## Translation conventions

1. **Preserve interpolation tokens verbatim** — `$query$`, `$totalResults$`, `$contentType$`, `<strong>…</strong>`, escaped quotes `\"…\"`. They are runtime placeholders; never translate or reorder them out of context.
2. **Match register and tone** — keep e-commerce conventions (e.g. Spanish "Ordenar por", not "Clasificar por"; Italian "Ordina per"). Hold one register across the whole header (see the source-of-truth note above).
3. **Match punctuation of the source** — if the English ends in a colon + space (`"Go to: "`), match that. If it ends in a period (`"products."`), match that. Trailing whitespace is meaningful.
4. **Lowercase/uppercase parity** — `text_products = "products."` is lowercase because it concatenates after a count; keep that. The `text_category_no_content_before` / `_after` pair wraps a count too — keep them grammatically consistent so the assembled sentence reads naturally in the target language.
5. **Empty strings** — if a token is `""` in the source (some languages don't need a "No" prefix), match the source intent rather than forcing a word in.
6. **Cross-check the surveyed storefront copy.** If the customer's site already uses specific wording for "Sort by", "Filters", "Clear all", etc., reuse it verbatim — operator consistency beats dictionary-perfect translation.

## Reference translations for common locales

The base languages HR has historically shipped (`da`, `sv`, `nl`, `no`, `fi`, `de`, `fr`) and the most common others — use as a quick aid when `translations.json` lacks an entry. **`translations.json` still wins where it has the token.**

| Token | English | `da` | `sv` | `de` | `fr` | `nl` | `es` | `it` |
|---|---|---|---|---|---|---|---|---|
| `text_sorting_title` | Sort by | Sorter efter | Sortera efter | Sortieren nach | Trier par | Sorteer op | Ordenar por | Ordina per |
| `text_go_directly_to` | Go to:  | Gå til:  | Gå till:  | Gehe zu:  | Aller à:  | Ga naar:  | Ir a:  | Vai a:  |
| `text_product_title` / `text_products_title` | Products | Produkter | Produkter | Produkte | Produits | Producten | Productos | Prodotti |
| `text_filters_selected_clear_button` | Clear all filters | Fjern alle filtre | Rensa alla filter | Alle Filter entfernen | Effacer tous les filtres | Alle filters wissen | Borrar todos los filtros | Cancella tutti i filtri |
| `text_products` | products. | produkter. | produkter. | Produkte. | produits. | producten. | productos. | prodotti. |
| `text_category_no_content_before` | No | Ingen | Inga | Keine | Aucun | Geen | No se | Nessun |
| `text_category_no_content_after` | were found. | blev fundet. | hittades. | gefunden. | trouvé. | gevonden. | encontró. | trovato. |
| `label_filters` | Filters | Filtre | Filter | Filter | Filtres | Filters | Filtros | Filtri |
| `label_clear_filter` | Clear filter | Ryd filter | Rensa filter | Filter löschen | Effacer le filtre | Filter wissen | Borrar filtro | Cancella filtro |
| `label_skip_to_products` | Skip to products | Gå til produkter | Gå till produkter | Zu den Produkten | Aller aux produits | Ga naar producten | Ir a los productos | Vai ai prodotti |
| `label_skip_to_input` | Skip to search input | Gå til søgefeltet | Gå till sökfältet | Zum Sucheingabefeld | Aller au champ de recherche | Ga naar zoekveld | Ir al campo de búsqueda | Vai al campo di ricerca |
| `label_close_search` | Close search | Luk søgning | Stäng sökning | Suche schließen | Fermer la recherche | Sluit zoeken | Cerrar búsqueda | Chiudi ricerca |
| `text_type_to_search` | Search among 10,000 products... | Søg blandt 10.000 produkter ... | Sök bland 10 000 produkter ... | Suche unter 10.000 Produkten ... | Rechercher parmi 10 000 produits ... | Zoek tussen 10.000 producten... | Buscar entre 10.000 productos... | Cerca tra 10.000 prodotti... |
| `result_subtitle` | The search `<strong>"$query$"</strong>` matches `<strong>$totalResults$</strong>` `$contentType$` | Søgningen `<strong>"$query$"</strong>` gav `<strong>$totalResults$</strong>` `$contentType$` | Sökningen `<strong>"$query$"</strong>` matchar `<strong>$totalResults$</strong>` `$contentType$` | Die Suche `<strong>"$query$"</strong>` ergab `<strong>$totalResults$</strong>` `$contentType$` | La recherche `<strong>"$query$"</strong>` correspond à `<strong>$totalResults$</strong>` `$contentType$` | De zoekopdracht `<strong>"$query$"</strong>` komt overeen met `<strong>$totalResults$</strong>` `$contentType$` | La búsqueda `<strong>"$query$"</strong>` coincide con `<strong>$totalResults$</strong>` `$contentType$` | La ricerca `<strong>"$query$"</strong>` corrisponde a `<strong>$totalResults$</strong>` `$contentType$` |
| `text_synonym_only_suggested` | We didn't find exactly what you were looking for, but here are some products you might find interesting: | Vi fandt ikke præcis det, du søgte efter, men her er nogle produkter, du måske finder interessante: | Vi hittade inte exakt det du sökte, men här är några produkter du kan tycka är intressanta: | Wir haben nicht genau das gefunden, wonach Sie gesucht haben, aber hier sind einige Produkte, die Sie interessieren könnten: | Nous n'avons pas trouvé exactement ce que vous cherchiez, mais voici quelques produits qui pourraient vous intéresser : | We hebben niet precies gevonden wat u zocht, maar hier zijn enkele producten die u interessant kunt vinden: | No encontramos exactamente lo que buscabas, pero aquí hay algunos productos que podrían interesarte: | Non abbiamo trovato esattamente ciò che cercavi, ma ecco alcuni prodotti che potrebbero interessarti: |
| `text_synonym_mixed` | We have expanded the search with more products that you might find interesting. | Vi har udvidet søgningen med flere produkter du måske finder interessante. | Vi har utökat sökningen med fler produkter som du kan tycka är intressanta. | Wir haben die Suche um weitere Produkte erweitert, die Sie interessieren könnten. | Nous avons élargi la recherche avec d'autres produits qui pourraient vous intéresser. | We hebben de zoekopdracht uitgebreid met meer producten die u interessant kunt vinden. | Hemos ampliado la búsqueda con más productos que pueden interesarte. | Abbiamo ampliato la ricerca con altri prodotti che potrebbero interessarti. |

For locales not in this table and not in `translations.json` (`pt`, `pl`, `cs`, `hu`, `tr`, `el`, `ro`, `bg`, `lt`, `lv`, `et`, …), translate using the same conventions and **add a line to MISSING DATA**: `Translation header hand-translated for <locale>; operator should verify e-commerce wording matches the customer's site.`

## Legacy multi-variant headers

If you ever read a design whose header still carries the old `__<Language>` variant form (`text_sorting_title__Danish = …`, etc. — older base-template-derived configs), reduce it to the modern flat form: keep one value per token in the target locale and **delete every `__<Language>` line**. The output is identical to the translate-in-place result above; you just had to pick the value from an existing variant instead of translating it.

## Self-check

- [ ] Every user-facing `{# text … #}` value is in the target locale (or left English for an English site).
- [ ] No `__<Language>` variant lines remain (none should have been present; if a legacy header had them, they're gone).
- [ ] All `{# boolean … #}`, `{# color … #}`, `{# number … #}`, `{# section … #}` declarations preserved unchanged.
- [ ] `webshop_name`, `header_logo_url`, and theme color tokens set to the customer's real values, not base placeholders (see `branding-and-header.md`).
- [ ] All `$query$`, `$totalResults$`, `$contentType$`, `<strong>…</strong>` interpolations preserved verbatim.
- [ ] Key order and group spacing preserved; header is followed by the Liquid body exactly as in the source design.
