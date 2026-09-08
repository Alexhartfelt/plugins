# Search — General (platform-agnostic)
Platform-agnostic Hello Retail Search snippets. These use HR's own `.hr-*` / `.aw-*` classes and template engine — they work on any platform once HR JS is installed.

For platform-specific variants (Shopify URL patterns, Magento selectors, etc.) see the sibling files.

---

### _Mobile Grid Search_

Layout for the mobile overlay search so product tiles stack two-per-row with rounded corners.

```css
.hr-tab-wrapper {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
}
.hr-tab-body[data-tab='category'] .hr-tab-wrapper {
    display: block;
}

.hr-overlay-search .hr-search-overlay-product {
    padding: 10px;
    position: relative;
    background-color: #ffffff;
    border-radius: 12px;
    -webkit-border-radius: 12px;
    -moz-border-radius: 12px;
    flex-basis: 42%;
    flex-direction: column;
    display: flex;
    margin: 5px auto;
}

.hr-row {
    display: flex;
    flex-direction: column;
    width: 100%;
}

.hr-col-img {
    flex-basis: 120px;
}

.hr-overlay-search > .hr-tabs > .hr-tab-content .hr-tab-header {
    flex-basis: 100%;
}
```

**Variant B — CSS grid, exact 2 columns.** ⚠️ **Old (legacy) mobile overlay searches only** — i.e. designs whose default template has no built-in grid option. Newer search templates ship with a native grid layout option; when the design already offers one, use that instead of this CSS override. Converts the product tab to a strict two-per-row grid without touching the tile markup or the other tabs. The `.hr-tab-header` (the "Søgningen gav …" subtitle) sits inside the same wrapper, so it's lifted out of the grid flow with absolute positioning and the wrapper reserves its height via `margin-top`. Pairs well with a card-style tile (e.g. one ported from the customer's desktop search); if the tiles have their own `margin-bottom`, zero it out so it doesn't stack with the grid `gap`.

```css
.hr-tab-body[data-tab="product"] .hr-tab-wrapper {
    display: grid;
    grid-template-columns: calc(50% - 5px) calc(50% - 5px);
    gap: 10px;
    margin-top: 50px;
    position: relative;
}

.hr-tab-body[data-tab="product"] .hr-tab-wrapper .hr-tab-header {
    position: absolute;
    top: -50px;
    width: 100%;
}
```

---

### _Add redirects in grid search_

The standard `search_redirects` module only attaches in overlay search by default. Use this to wire it into the grid search input as well.

```javascript
// Add to the top
import "search_redirects";

// Add above engine_options
document.querySelector(".aw-search-input").addEventListener('keyup', (event) => {
    search_redirects.match_and_go(event.target.value, key)
});
```

---

### _Filter Sorting — DESKTOP_

Sort filter values (sizes, colors, etc.) deterministically: numeric / alphabetical / user-assorted with per-filter `=asc` / `=desc` overrides.

```javascript
// Function
/* text */ var desktop_default_filters_to_sort = ""; // =asc or =desc to control the individual filters sorting directive.
/* text */ var desktop_extraData_filters_to_sort = "length,buckle,width=desc"; // =asc or =desc to control the individual filters sorting directive.
/* text */ var desktop_extraDataList_filters_to_sort = ""; // =asc or =desc to control the individual filters sorting directive.
/* text */ var desktop_add_to_assorted_filters_list = ""; // add label names here in the exact order that they should be sorted in (this will priority sort the provided label names and won't be sorted numerically or alphabetical).
desktop_default_filters_to_sort = desktop_default_filters_to_sort.split(",");
desktop_extraData_filters_to_sort = desktop_extraData_filters_to_sort.split(",");
desktop_extraDataList_filters_to_sort = desktop_extraDataList_filters_to_sort.split(",");
desktop_add_to_assorted_filters_list = desktop_add_to_assorted_filters_list.toLowerCase().split(",");
/* boolean */ var desktop_ascending_filter_sorting = true; // global sorting directive used if no =asc / =desc sorting directive is present for the individual filter.
/* boolean */ var desktop_numbers_first_in_filters = true; // control whether the labels considered to be numerical values should be shown before or after the alphabetical labels.
/* boolean */ var desktop_console_debug = false;
/* text */ var desktop_filter_title_start_with_number_or_contain_number_or_only_number = "start_with_number".toLowerCase(); // start_with_number / contain_number / only_number: control when a the labels in filter dropdowns should be considered numerical.
function sortFiltersDesktop(parentClass, sortingDirective) {
    console.time(`${parentClass} filtering took`);
    var numDesktop = [];
    var alphDesktop = [];
    var assortedDesktop = [];
    if (!document.querySelector(parentClass)) {
        if (desktop_console_debug) {
            console.log(`"${parentClass}" is not a valid filter selector and will not be sorted.`);
        }
        return;
    }
    const parentDesktop = document.querySelector(parentClass);
    var divsDesktop;

    sortingDirective ? parentDesktop.setAttribute("sorting-directive", sortingDirective) : parentDesktop.setAttribute("sorting-directive", "default");
    parentClass.includes("hierarchies") ? divsDesktop = [...parentDesktop.querySelectorAll(`${parentClass} li`)] : divsDesktop = [...parentDesktop.querySelectorAll(`${parentClass} label`)];

    divsDesktop.forEach(function (label) {
        var titleDesktop = label.querySelector(".aw-filter-tag-title").textContent.trim();
        if (desktop_add_to_assorted_filters_list != "") {
            var index = desktop_add_to_assorted_filters_list.indexOf(titleDesktop.toLowerCase());
            if (index != -1) {
                label.setAttribute("user-sorting", index);
            }
        };
        if (label.hasAttribute("user-sorting")) {
            assortedDesktop.push(label);
        }
        else if ((titleDesktop.match(/[^\d]*(\d+).*/) && desktop_filter_title_start_with_number_or_contain_number_or_only_number == "contain_number") || (titleDesktop.match(/^(\d+).*/) && desktop_filter_title_start_with_number_or_contain_number_or_only_number == "start_with_number") || (titleDesktop.match(/^\d+$/) && desktop_filter_title_start_with_number_or_contain_number_or_only_number == "only_number")) {
            if (desktop_filter_title_start_with_number_or_contain_number_or_only_number == "start_with_number") {
                label.setAttribute("num-sorting", titleDesktop.replace(/^(\d+).*/, "$1"));
                numDesktop.push(label);
            }
            else if (desktop_filter_title_start_with_number_or_contain_number_or_only_number == "contain_number") {
                label.setAttribute("num-sorting", titleDesktop.replace(/[^\d]*(\d+).*/, "$1"));
                numDesktop.push(label);
            }
            else {
                label.setAttribute("num-sorting", titleDesktop);
                numDesktop.push(label);
            }
        }
        else {
            label.setAttribute("alph-sorting", titleDesktop.replace(/\d+/, ""));
            alphDesktop.push(label);
        }
    });

    numDesktop.sort(function (a, b) {
        if (sortingDirective) {
            if (sortingDirective == "asc") {
                return a.getAttribute("num-sorting") - b.getAttribute("num-sorting");
            }
            else {
                return b.getAttribute("num-sorting") - a.getAttribute("num-sorting");
            }
        }
        else {
            if (desktop_ascending_filter_sorting) {
                return a.getAttribute("num-sorting") - b.getAttribute("num-sorting");
            }
            else {
                return b.getAttribute("num-sorting") - a.getAttribute("num-sorting");
            }
        }
    });
    alphDesktop.sort(function (a, b) {
        if (sortingDirective) {
            if (sortingDirective == "asc") {
                return (a.getAttribute("alph-sorting").toLowerCase() > b.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
            else {
                return (b.getAttribute("alph-sorting").toLowerCase() > a.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
        }
        else {
            if (desktop_ascending_filter_sorting) {
                return (a.getAttribute("alph-sorting").toLowerCase() > b.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
            else {
                return (b.getAttribute("alph-sorting").toLowerCase() > a.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
        }
    });
    assortedDesktop.sort(function (a, b) {
        if (sortingDirective) {
            if (sortingDirective == "asc") {
                return a.getAttribute("user-sorting") - b.getAttribute("user-sorting");
            }
            else {
                return b.getAttribute("user-sorting") - a.getAttribute("user-sorting");
            }
        }
        else {
            if (desktop_ascending_filter_sorting) {
                return a.getAttribute("user-sorting") - b.getAttribute("user-sorting");
            }
            else {
                return b.getAttribute("user-sorting") - a.getAttribute("user-sorting");
            }
        }
    });
    if (desktop_numbers_first_in_filters) {
        assortedDesktop.forEach(function (div) { parentDesktop.append(div); });
        numDesktop.forEach(function (div) { parentDesktop.append(div); });
        alphDesktop.forEach(function (div) { parentDesktop.append(div); });
    }
    else {
        assortedDesktop.forEach(function (div) { parentDesktop.append(div); });
        alphDesktop.forEach(function (div) { parentDesktop.append(div); });
        numDesktop.forEach(function (div) { parentDesktop.append(div); });
    }
    console.timeEnd(`${parentClass} filtering took`);
}

// Invocation
if (desktop_default_filters_to_sort != "") {
    desktop_default_filters_to_sort.forEach(function (filter) {
        var sortingDirective = filter.includes("=") ? filter.split("=").pop() : false;
        var filter = filter.includes("=") ? filter.split("=").shift() : filter;
        var filterStructured = `[data-filter='${filter}']`;
        filter == "hierarchies" ? sortFiltersDesktop(`${filterStructured} .aw-filter-list`, sortingDirective) : sortFiltersDesktop(`${filterStructured} .aw-filter-tag-list`, sortingDirective);
    });
}

if (desktop_extraData_filters_to_sort != "") {
    desktop_extraData_filters_to_sort.forEach(function (filter) {
        var sortingDirective = filter.includes("=") ? filter.split("=").pop() : false;
        var filter = filter.includes("=") ? filter.split("=").shift() : filter;
        var filterStructured = `[data-filter='extraData.${filter}']`;
        sortFiltersDesktop(`${filterStructured} .aw-filter-tag-list`, sortingDirective);
    });
}

if (desktop_extraDataList_filters_to_sort != "") {
    desktop_extraDataList_filters_to_sort.forEach(function (filter) {
        var sortingDirective = filter.includes("=") ? filter.split("=").pop() : false;
        var filter = filter.includes("=") ? filter.split("=").shift() : filter;
        var filterStructured = `[data-filter='extraDataList.${filter}']`;
        sortFiltersDesktop(`${filterStructured} .aw-filter-tag-list`, sortingDirective);
    });
}
```

---

### _Filter Sorting — MOBILE_

Mobile counterpart of the desktop sort. Targets the `.hr-search-overlay-filter-wrap` containers.

```javascript
// Function
/* text */ var mobile_default_filters_to_sort = "brand,hierarchies";
/* text */ var mobile_extraData_filters_to_sort = "";
/* text */ var mobile_extraDataList_filters_to_sort = "size=desc,color=asc";
/* text */ var mobile_add_to_assorted_filters_list = "36,42";
mobile_default_filters_to_sort = mobile_default_filters_to_sort.split(",");
mobile_extraData_filters_to_sort = mobile_extraData_filters_to_sort.split(",");
mobile_extraDataList_filters_to_sort = mobile_extraDataList_filters_to_sort.split(",");
mobile_add_to_assorted_filters_list = mobile_add_to_assorted_filters_list.toLowerCase().split(",");
/* boolean */ var mobile_ascending_filter_sorting = true;
/* boolean */ var mobile_numbers_first_in_filters = true;
/* boolean */ var mobile_console_debug = false;
/* text */ var mobile_filter_title_start_with_number_or_contain_number_or_only_number = "only_number".toLowerCase();
function sortFiltersMobile(parentClass, sortingDirective) {
    var numMobile = [];
    var alphMobile = [];
    var assortedMobile = [];
    if (!document.querySelector(parentClass)) {
        if (mobile_console_debug) {
            console.log(`"${parentClass}" is not a valid filter selector and will not be sorted.`);
        }
        return;
    }
    const parentMobile = document.querySelector(parentClass);
    var divsMobile;

    sortingDirective ? parentMobile.setAttribute("sorting-directive", sortingDirective) : parentMobile.setAttribute("sorting-directive", "default");
    parentClass.includes("hierarchies") ? divsMobile = [...parentMobile.querySelectorAll(`${parentClass} li`)] : divsMobile = [...parentMobile.querySelectorAll(`${parentClass} label`)];

    divsMobile.forEach(function (label) {
        var titleMobile = label.querySelector(".aw-filter-tag-title").textContent.trim();
        if (mobile_add_to_assorted_filters_list != "") {
            var index = mobile_add_to_assorted_filters_list.indexOf(titleMobile.toLowerCase());
            if (index != -1) {
                label.setAttribute("user-sorting", index);
            }
        };
        if (label.hasAttribute("user-sorting")) {
            assortedMobile.push(label);
        }
        else if ((titleMobile.match(/[^\d]*(\d+).*/) && mobile_filter_title_start_with_number_or_contain_number_or_only_number == "contain_number") || (titleMobile.match(/^(\d+).*/) && mobile_filter_title_start_with_number_or_contain_number_or_only_number == "start_with_number") || (titleMobile.match(/^\d+$/) && mobile_filter_title_start_with_number_or_contain_number_or_only_number == "only_number")) {
            if (mobile_filter_title_start_with_number_or_contain_number_or_only_number == "start_with_number") {
                label.setAttribute("num-sorting", titleMobile.replace(/^(\d+).*/, "$1"));
                numMobile.push(label);
            }
            else if (mobile_filter_title_start_with_number_or_contain_number_or_only_number == "contain_number") {
                label.setAttribute("num-sorting", titleMobile.replace(/[^\d]*(\d+).*/, "$1"));
                numMobile.push(label);
            }
            else {
                label.setAttribute("num-sorting", titleMobile);
                numMobile.push(label);
            }
        }
        else {
            label.setAttribute("alph-sorting", titleMobile.replace(/\d+/, ""));
            alphMobile.push(label);
        }
    });

    numMobile.sort(function (a, b) {
        if (sortingDirective) {
            if (sortingDirective == "asc") {
                return a.getAttribute("num-sorting") - b.getAttribute("num-sorting");
            }
            else {
                return b.getAttribute("num-sorting") - a.getAttribute("num-sorting");
            }
        }
        else {
            if (mobile_ascending_filter_sorting) {
                return a.getAttribute("num-sorting") - b.getAttribute("num-sorting");
            }
            else {
                return b.getAttribute("num-sorting") - a.getAttribute("num-sorting");
            }
        }
    });
    alphMobile.sort(function (a, b) {
        if (sortingDirective) {
            if (sortingDirective == "asc") {
                return (a.getAttribute("alph-sorting").toLowerCase() > b.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
            else {
                return (b.getAttribute("alph-sorting").toLowerCase() > a.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
        }
        else {
            if (mobile_ascending_filter_sorting) {
                return (a.getAttribute("alph-sorting").toLowerCase() > b.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
            else {
                return (b.getAttribute("alph-sorting").toLowerCase() > a.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
        }
    });
    assortedMobile.sort(function (a, b) {
        if (sortingDirective) {
            if (sortingDirective == "asc") {
                return a.getAttribute("user-sorting") - b.getAttribute("user-sorting");
            }
            else {
                return b.getAttribute("user-sorting") - a.getAttribute("user-sorting");
            }
        }
        else {
            if (mobile_ascending_filter_sorting) {
                return a.getAttribute("user-sorting") - b.getAttribute("user-sorting");
            }
            else {
                return b.getAttribute("user-sorting") - a.getAttribute("user-sorting");
            }
        }

    });
    if (mobile_numbers_first_in_filters) {
        assortedMobile.forEach(function (div) { parentMobile.append(div); });
        numMobile.forEach(function (div) { parentMobile.append(div); });
        alphMobile.forEach(function (div) { parentMobile.append(div); });
    }
    else {
        assortedMobile.forEach(function (div) { parentMobile.append(div); });
        alphMobile.forEach(function (div) { parentMobile.append(div); });
        numMobile.forEach(function (div) { parentMobile.append(div); });
    }
}

// Invocation
if (mobile_default_filters_to_sort != "") {
    mobile_default_filters_to_sort.forEach(function (filter) {
        var sortingDirective = filter.includes("=") ? filter.split("=").pop() : false;
        var filter = filter.includes("=") ? filter.split("=").shift() : filter;
        var filterStructured = `.hr-search-overlay-filter-wrap[data-filter='${filter}']`;
        filter == "hierarchies" ? sortFiltersMobile(`${filterStructured} .aw-filter-list`, sortingDirective) : sortFiltersMobile(`${filterStructured} .aw-filter-tag-list`, sortingDirective);
    });
}

if (mobile_extraData_filters_to_sort != "") {
    mobile_extraData_filters_to_sort.forEach(function (filter) {
        var sortingDirective = filter.includes("=") ? filter.split("=").pop() : false;
        var filter = filter.includes("=") ? filter.split("=").shift() : filter;
        var filterStructured = `.hr-search-overlay-filter-wrap[data-filter='extraData.${filter}']`;
        sortFiltersMobile(`${filterStructured} .aw-filter-tag-list`, sortingDirective);
    });
}

if (mobile_extraDataList_filters_to_sort != "") {
    mobile_extraDataList_filters_to_sort.forEach(function (filter) {
        var sortingDirective = filter.includes("=") ? filter.split("=").pop() : false;
        var filter = filter.includes("=") ? filter.split("=").shift() : filter;
        var filterStructured = `.hr-search-overlay-filter-wrap[data-filter='extraDataList.${filter}']`;
        sortFiltersMobile(`${filterStructured} .aw-filter-tag-list`, sortingDirective);
    });
}
```

---

### _Filter Sorting — PAGES_

Same idea as desktop/mobile but for Hello Retail **Pages** (category/brand). Uses `[data-filter-name='...']` and Danish filter names by default.

```javascript
// Function
var pages_default_filters_to_sort = "Mærke,Størrelse,Farve";
var pages_add_to_assorted_filters_list = "ONE SIZE,XXS,XXS/XS,XS,XS/S,S,S/M,M,M/L,L,L/XL,XL,XXL,3XL";
pages_default_filters_to_sort = pages_default_filters_to_sort.split(",");
pages_add_to_assorted_filters_list = pages_add_to_assorted_filters_list.toLowerCase().split(",");
var pages_ascending_filter_sorting = true;
var pages_numbers_first_in_filters = true;
var pages_console_debug = true;
var pages_filter_title_start_with_number_or_contain_number_or_only_number = "start_with_number".toLowerCase();
function sortFiltersPages(parentClass, sortingDirective) {
    var numPages = [];
    var alphPages = [];
    var assortedPages = [];
    if (!document.querySelector(parentClass)) {
        if (pages_console_debug) {
            console.log(`"${parentClass}" is not a valid filter selector and will not be sorted.`);
        }
        return;
    }
    const parentPages = document.querySelector(parentClass);
    var divsPages;

    sortingDirective ? parentPages.setAttribute("sorting-directive", sortingDirective) : parentPages.setAttribute("sorting-directive", "default");
    parentClass.includes("Kategorier") ? divsPages = [...parentPages.querySelectorAll(`${parentClass} li`)] : divsPages = [...parentPages.querySelectorAll(`${parentClass} label`)];

    divsPages.forEach(function (label) {
        var titlePages = label.querySelector(".aw-filter-tag-title").textContent.trim();
        if (pages_add_to_assorted_filters_list != "") {
            var index = pages_add_to_assorted_filters_list.indexOf(titlePages.toLowerCase());
            if (index != -1) {
                label.setAttribute("user-sorting", index);
            }
        };
        if (label.hasAttribute("user-sorting")) {
            assortedPages.push(label);
        }
        else if ((titlePages.match(/[^\d]*(\d+).*/) && pages_filter_title_start_with_number_or_contain_number_or_only_number == "contain_number") || (titlePages.match(/^(\d+).*/) && pages_filter_title_start_with_number_or_contain_number_or_only_number == "start_with_number") || (titlePages.match(/^\d+$/) && pages_filter_title_start_with_number_or_contain_number_or_only_number == "only_number")) {
            if (pages_filter_title_start_with_number_or_contain_number_or_only_number == "start_with_number") {
                label.setAttribute("num-sorting", titlePages.replace(/^(\d+).*/, "$1"));
                numPages.push(label);
            }
            else if (pages_filter_title_start_with_number_or_contain_number_or_only_number == "contain_number") {
                label.setAttribute("num-sorting", titlePages.replace(/[^\d]*(\d+).*/, "$1"));
                numPages.push(label);
            }
            else {
                label.setAttribute("num-sorting", titlePages);
                numPages.push(label);
            }
        }
        else {
            label.setAttribute("alph-sorting", titlePages.replace(/\d+/, ""));
            alphPages.push(label);
        }
    });

    numPages.sort(function (a, b) {
        if (sortingDirective) {
            if (sortingDirective == "asc") {
                return a.getAttribute("num-sorting") - b.getAttribute("num-sorting");
            }
            else {
                return b.getAttribute("num-sorting") - a.getAttribute("num-sorting");
            }
        }
        else {
            if (pages_ascending_filter_sorting) {
                return a.getAttribute("num-sorting") - b.getAttribute("num-sorting");
            }
            else {
                return b.getAttribute("num-sorting") - a.getAttribute("num-sorting");
            }
        }
    });
    alphPages.sort(function (a, b) {
        if (sortingDirective) {
            if (sortingDirective == "asc") {
                return (a.getAttribute("alph-sorting").toLowerCase() > b.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
            else {
                return (b.getAttribute("alph-sorting").toLowerCase() > a.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
        }
        else {
            if (pages_ascending_filter_sorting) {
                return (a.getAttribute("alph-sorting").toLowerCase() > b.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
            else {
                return (b.getAttribute("alph-sorting").toLowerCase() > a.getAttribute("alph-sorting").toLowerCase() ? 1 : -1);
            }
        }
    });
    assortedPages.sort(function (a, b) {
        if (sortingDirective) {
            if (sortingDirective == "asc") {
                return a.getAttribute("user-sorting") - b.getAttribute("user-sorting");
            }
            else {
                return b.getAttribute("user-sorting") - a.getAttribute("user-sorting");
            }
        }
        else {
            if (pages_ascending_filter_sorting) {
                return a.getAttribute("user-sorting") - b.getAttribute("user-sorting");
            }
            else {
                return b.getAttribute("user-sorting") - a.getAttribute("user-sorting");
            }
        }
    });
    if (pages_numbers_first_in_filters) {
        assortedPages.forEach(function (div) { parentPages.append(div); });
        numPages.forEach(function (div) { parentPages.append(div); });
        alphPages.forEach(function (div) { parentPages.append(div); });
    }
    else {
        assortedPages.forEach(function (div) { parentPages.append(div); });
        alphPages.forEach(function (div) { parentPages.append(div); });
        numPages.forEach(function (div) { parentPages.append(div); });
    }
}

// Invocation
if (pages_default_filters_to_sort != "") {
    pages_default_filters_to_sort.forEach(function (filter) {
        var sortingDirective = filter.includes("=") ? filter.split("=").pop() : false;
        var filter = filter.includes("=") ? filter.split("=").shift() : filter;
        var filterStructured = `[data-filter-name='${filter}']`;
        filter == "Kategorier" ? sortFiltersPages(`${filterStructured} .aw-filter-list`, sortingDirective) : sortFiltersPages(`${filterStructured} .aw-filter-tag-list`, sortingDirective);
    });
}
```

---

### _Hide / Show filter based on input_

Toggle a filter container based on whether the search input matches a trigger word. Place the snippet on the last line of the `load_more_results` function. Works with Overlay out of the box — rename `data-filter` and `TRIGGERWORD` as needed.

```javascript
// Placement of snippet: last line in the function named "load_more_results"
// Notes: This works with Overlay out of the box. Just rename the data-filter to the given filter, and the matched value of the input-field to trigger the filter.
var inputValue = document.querySelector(".hr-search > input").value
var mistralFilterContainer = document.querySelector(".aw-filter__single-wrapper[data-filter='extraData.filterName']");

if (document.querySelector(".hr-search > input").value.match(/.*TRIGGERWORD.*/i)) {
    mistralFilterContainer.style.display = "block";
} else {
    mistralFilterContainer.style.display = "none";
}
```

---

### _Collapse a long filter row behind a "More filters" toggle_

When a config has many facets (9+ is common once size / colour / brand / gender and a few custom fields are all indexed) the filter row eats the fold. Show the first N, hide the rest behind a toggle. The collapse is **CSS-driven** so the extra filters never flash before JS runs, and the button is **authored in the template** so it exists regardless of where the JS call site sits.

**1. `resultTemplate`** — labels as design fields, button as the **last child** of the filter `<ul>`:

```liquid
{# text label_more_filters = "More filters" #}
{# text label_fewer_filters = "Fewer filters" #}
```

```liquid
                {% endif %}
                <li class="hr-show-filters-item">
                    <button type="button" class="hr-show-filters-btn" aria-expanded="false" data-label-more="{{ label_more_filters }}" data-label-fewer="{{ label_fewer_filters }}">{{ label_more_filters }}</button>
                </li>
            </ul>
```

**2. `resultStyles`** — default-collapsed, plus the expanded override. `N = 4` here, so `n+5`:

```css
.hr-overlay-search .aw-full-search-results__filter-wrapper li.aw-filter__single-wrapper:nth-child(n+5):not(.aw-filter__sorting-wrapper) {
	display: none;
}

.hr-overlay-search .aw-full-search-results__filter-wrapper.hr-filters-expanded li.aw-filter__single-wrapper:nth-child(n+5) {
	display: block;
}

.hr-overlay-search .hr-show-filters-item {
	display: flex;
	align-items: center;
	list-style-type: none;
}
```

Style `.hr-show-filters-btn` as the **shop's own** "show more" / secondary button (copy its computed `background` / `border` / `radius` / font). A plain underlined text link reads as body copy and gets reported as "the toggle isn't implemented".

**3. `initializationCode`** — module-level state, then call it wherever `sortFilters()` is called (inside the `yield_template` callback, i.e. once per non-append render):

```javascript
/* number */ var visible_filter_count = 4;
var filters_expanded = false;

function limit_filters() {
	if (!overlay) {
		return;
	}
	var wrapper = overlay.querySelector(".hr-filters .aw-full-search-results__filter-wrapper");
	var item = wrapper ? wrapper.querySelector(".hr-show-filters-item") : null;
	var button = item ? item.querySelector(".hr-show-filters-btn") : null;
	if (!button) {
		return;
	}
	var collapsible = Array.prototype.slice.call(
			wrapper.querySelectorAll(".aw-filter__single-wrapper:not(.aw-filter__sorting-wrapper)")
	);
	var extra = collapsible.slice(visible_filter_count);
	if (!extra.length) {
		item.style.display = "none";
		return;
	}
	if (extra.some(function(filter) { return filter.querySelector(".hr-selected-filter-count"); })) {
		filters_expanded = true;
	}

	function apply_state() {
		wrapper.classList.toggle("hr-filters-expanded", filters_expanded);
		button.textContent = filters_expanded ? button.dataset.labelFewer : button.dataset.labelMore;
		button.setAttribute("aria-expanded", filters_expanded ? "true" : "false");
	}

	button.addEventListener("click", function() {
		filters_expanded = !filters_expanded;
		apply_state();
	});
	apply_state();
}
```

**Gotchas**

- **Exclude the sorting wrapper.** `sorting.asTagList` renders as the **last** `<li>`, so a blunt `:nth-child(n+5)` buries "Sort by" — a primary control — as soon as there are 4+ filters. Both the CSS and the JS above skip `.aw-filter__sorting-wrapper`.
- **`filters_expanded` must live outside the render.** `.hr-results` is `.remove()`d and rebuilt on every non-append `load_more_results(false)`, so a variable scoped inside the callback resets on each filter click and the panel snaps shut under the visitor.
- **Auto-expand when a hidden filter is active** (the `.hr-selected-filter-count` check) — otherwise the visitor filters by a facet and then can't see it.
- **Specificity:** the expanded rule needs the same `:nth-child(n+5)` as the collapse rule (otherwise it loses at `(0,4,1)` vs `(0,5,1)`) **and** must come later in the file.
- **Keep the two numbers in sync** — JS `visible_filter_count = N`, CSS `nth-child(n+N+1)`.
- `:nth-child` counts **all** `<li>` children, so keep the toggle's `<li>` last.
- Hide the toggle when there is nothing to expand, or it sits there doing nothing on narrow result sets.

---

### _Remove unwanted sorting ascending or descending values_

Strip specific sort options (e.g. "Price ascending") from the sort dropdown.

> Important: the label to be removed should literally match `THISSHOULDBEREMOVED` (replace with the actual label text).

```javascript
// Example - Line 135 JavaScript Estella.nl

document.querySelectorAll(".aw-sorting-tag-list label").forEach(function(item){
    if(item.textContent == "THISSHOULDBEREMOVED"){
        item.remove();
    }
})
```

---

### _Remove customer's page scroll when Embedded search is open_

Lock body scroll behind the embedded search overlay.

```css
.hr-search-disable-scroll{
    height: 100vh !important;
    width: 100vw !important;
    overflow: hidden !important;
}
```

---

### _Fix scroll in search_

Allow vertical scrolling inside the search overlay when content exceeds viewport.

```css
max-height: 100vh;
overflow: scroll;
```

---

### _Hide scrollbar from Embedded searches narrower than the viewport_

Cleaner look on webkit browsers.

```css
.hr-overlay-search::-webkit-scrollbar {
    width: 0 !important;
}
```

---

### _Remove cross (X) in desktop search input_

Cross-browser hide of the native "clear" icon on `<input type="search">`.

```css
input[type=search]::-ms-clear {
    display: none;
    width: 0;
    height: 0;
}
input[type=search]::-ms-reveal {
    display: none;
    width: 0;
    height: 0;
}
input[type="search"]::-webkit-search-decoration,
input[type="search"]::-webkit-search-cancel-button,
input[type="search"]::-webkit-search-results-button,
input[type="search"]::-webkit-search-results-decoration {
    display: none;
}
```

---

### _Reset form event listener (Search)_

If the customer's theme binds its own handler to the search button and breaks HR's, clone-and-replace to strip listeners.

```javascript
var searchBtn = document.querySelector(".header-search");
searchBtn.replaceWith(searchBtn.cloneNode(true));
```

---

### _Add hierarchy path to category content template_

Renders breadcrumbs above content items in search results. Remove `limit : 1` to show all hierarchy levels.

```liquid
<span class="hr-search-overlay-content-hierarchy-wrapper">
    {% for level in ctnt.hierarchy limit : 1 %}
    {% if level != "" and level != current_content_item.title %}
    <span class="hr-search-overlay-content-category-hierarchy-category">{{ level }}</span>
    {% unless forloop.last %}
    <span class="hr-search-overlay-content-hierarchy-divider">›</span>
    {% endunless %}
    {% endif %}
    {% endfor %}
</span>
```

```css
.hr-search-overlay-content-hierarchy-wrapper {
    display: block;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    font-size: .9em;
    color: #777;
}
```

---

### _Add filters in full search_

Can be added across all templates. *(No code recorded — add when next encountered.)*

---

### _Offset top — push HR overlay below the customer's fixed header_

Read the customer's header height on every viewport resize and apply it as `margin-top` on `.hr-overlay-search`. Use when the customer's header is `position: fixed` and HR's overlay would otherwise hide under it.

```javascript
window.addEventListener("resize", calculateOffset);
function calculateOffset() {
    const header = document.querySelector("#header");
    const _overlay = document.querySelector('.hr-overlay-search');
    if (_overlay && header) _overlay.style.marginTop = header.clientHeight + "px";
}
```

Adapt `#header` to the customer's actual header selector. Common ones: `header.site-header`, `#shopify-section-header`, `.site-navbar`, etc.

> For WooCommerce shops with the **demo store notice** (`.woocommerce-store-notice.demo_store`), use the dedicated MutationObserver variant in [woocommerce.md](./woocommerce.md) instead — that notice changes height when collapsed.

---

### _Highlight search term in category results_

Wrap matches of the search term in `<strong>` inside HR's category content tiles. Must be defined **inside the `activate()` function** so `searcher.search_term` is in scope.

```javascript
function categoryTextBold() {
    var searchInput = document.querySelector(".hr-search input");
    var categoryElements = document.querySelectorAll(".hr-search-overlay-content");
    var searchTerm = searcher.search_term;
    categoryElements.forEach(category => {
        var linkElement = category.querySelector(".hr-search-overlay-content-link");
        if (!linkElement) return;
        var originalText = linkElement.textContent;
        if (searchTerm !== "") {
            var regex = new RegExp(`(${searchTerm})`, "gi");
            linkElement.innerHTML = originalText.replace(regex, `<strong>$1</strong>`);
        }
    });
}
```

Call `categoryTextBold()` after results render.

**Seen on:** a customer storefront onboarding.

> ⚠️ If `searchTerm` could contain regex special characters (`.`, `*`, etc.), escape it first: `searchTerm.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")`.

---

### _Tile CSS parity — an empty CUSTOM_STYLING_BLOCK is a starting point, not the finish_

**The trap:** the verbatim-tile approach assumes that because we keep the customer's tile classes/markup byte-for-byte, the customer's own theme CSS will style it inside the HR overlay. **That assumption fails often.** When it does, you ship a tile that looks broken (classic symptom: product **titles wrap one letter per line** because the tile collapsed to ~0 width). Don't trust it — open the overlay, run a real search, and QA the rendered tile before calling an onboarding done.

**Why it fails (two recurring causes):**

1. **The theme styles the tile via an ancestor that the HR overlay doesn't reproduce.** Most grids put column width on the *grid item* (`ul.products > li`, `.list-collection > .data-product`, `.collection-product …`) using a direct-child relationship or a section-scoped ancestor. HR wraps every result in `.hr-search-overlay-product` and renders inside `.hr-products-container` — so the customer tile is no longer the grid item / no longer under that ancestor, and the width/layout rules never match. → Put the column width on `.hr-search-overlay-product` (make it `display:block`) and give the tile `width:100%`. If the theme rule is `.<section> .tile {…}`, add `<section>` to `.hr-products-container` (e.g. a theme that scopes its tile rules under a `.collection-product` ancestor).
2. **HR's base `search.css` overrides the theme.** It commonly forces, inside `.hr-overlay-search`: `text-align:center`, a fixed product-image height, `list-style`/padding resets (which kill or expose `::before`/`::after` dividers), and `display:flex` + padding on buy buttons. Your overrides usually need `!important` **and** sometimes a deeper selector (e.g. `footer.extra form button.cart-form-submit`) to win the cascade.

**The method — diff, don't guess.** Reactively tweaking CSS round after round wastes time. Instead, in the live overlay compare the **native category-page tile** against the **HR-rendered overlay tile** with `getComputedStyle`, element by element, and only override the properties that differ:

```js
// in DevTools / Chrome console on a page where the overlay is open
const o = document.querySelector('.hr-overlay-search .<tile-selector>');           // overlay tile
const n = [...document.querySelectorAll('.<tile-selector>')].find(t => !t.closest('.hr-overlay-search')); // native tile
const PROPS = ['display','flexDirection','float','width','height','aspectRatio','objectFit',
               'textAlign','padding','margin','listStyleType','borderTopWidth','borderLeftWidth'];
['', 'img', 'h3', '.price', 'button'].forEach(sel => {            // add the tile's real sub-selectors
  const a = sel ? n.querySelector(sel) : n, b = sel ? o.querySelector(sel) : o;
  if (!a || !b) return;
  const ca = getComputedStyle(a), cb = getComputedStyle(b);
  PROPS.forEach(p => ca[p] !== cb[p] && console.log(sel||'(root)', p, ':', ca[p], '→', cb[p]));
});
```

Every line it prints is a property to set back to the native value (scoped to `.hr-overlay-search`). Also check **pseudo-elements** (`getComputedStyle(el,'::before')`) and the **intrinsic image** (`img.naturalWidth/Height`, `currentSrc`) — feed images often differ in ratio from the storefront's fixed thumbnails. Keep hover/decoration pseudos you want (e.g. a `::before` hover card); hide only the divider pseudos and zero transparent gutter borders.

**QA checklist before shipping a Search tile:**

- [ ] Opened the overlay, ran a real query, and looked at the rendered tile (not just the Liquid).
- [ ] Titles wrap normally; tile fills its column; image ratio matches the storefront.
- [ ] Buy button / qty / badges aligned; no stray divider lines or uneven edges; hover state intact.
- [ ] Any CSS added is scoped to `.hr-overlay-search` (embedded: the embedded container) and never touches the storefront grid.
- [ ] CSS-only — no markup/class/attribute changes — so the theme's (often delegated) JS bindings keep working.
- [ ] Feature controls that need IDs (ATC, wishlist, Quick View) use an ID the **feed actually exposes** — verify, don't assume `productNumber` is the platform's numeric id.

> Platform specifics: [lightspeed.md](./lightspeed.md) (grid-ancestor collapse, divider pseudos, SKU-vs-numeric-id), [shopify.md](./shopify.md). Real builds: [client-scripts](../../client-scripts/README.md).

---

### _`show_vertical_link_content` — required for a content-feed tab to actually behave as a separate tab_

**Symptom:** a content-feed type (e.g. Category) is correctly configured via `search_updateLinkContent`, but on the storefront it doesn't show up as its own stable tab — it's missing, or only appears intermittently depending on what's typed.

**Cause:** the mobile-overlay base template has two tab-rendering modes controlled by the `show_vertical_link_content` boolean (declared in `resultTemplate`):

- **`false` ("horizontal" mode):** the `product-tab` button is statically hidden (`hr-hidden`) in the initial render, and a JS routine (`toggle_tab_visibility()`) only un-hides each tab — product **or** content-feed — once that tab has real, non-initial-content results for the current query. A content-feed tab can therefore look broken/absent even though the config is correct: it's gated behind "has this type returned real matches yet."
- **`true` ("vertical" mode):** no tab is statically hidden; every configured content type (plus Products) renders as a stable top-level tab from the very first render.

**Fix:** if the ask is "Category (or any content-feed type) needs to be its own separate tab," set `{# boolean show_vertical_link_content = true #}` in `resultTemplate` — no other template/JS change needed. Note this also changes how the content **links themselves** render inside the tab (vertical mode = full-width list rows with a hierarchy breadcrumb + chevron icon; horizontal mode = a horizontal-scrolling row of pill-shaped chips) — that's a visual trade-off to flag to the operator, not just a tab-visibility toggle.

**Seen on:** kalaskungen.com, 2026-08-25 (Overlay search mobile — EAA accessibility).

---

## Timeline
- 2026-05-19: Initial import from Taqi's Search cheat sheet (Notion export).
- 2026-05-21: Added Offset Top and Highlight-search-term-in-categories from Taqi's separate snippets.
- 2026-06-04: Added _Tile CSS parity_ — why an empty CUSTOM_STYLING_BLOCK isn't safe, the native-vs-overlay computed-style diff method, and a pre-ship QA checklist (from a Lightspeed onboarding).
- 2026-08-12: Added _Collapse a long filter row behind a "More filters" toggle_ — CSS-driven collapse + template-authored button, sorting-wrapper exclusion, state-across-rerender and specificity gotchas (source: desktop-embedded search onboarding).
- 2026-08-20: Added _Mobile Grid Search_ Variant B — strict 2-column CSS grid on the product tab with the tab header lifted out of grid flow; legacy templates only, use the native grid option where the design offers one (field-proven list→grid conversion of a live mobile overlay search).
- 2026-08-25: Added _`show_vertical_link_content` — required for a content-feed tab to actually behave as a separate tab_ (source: kalaskungen.com EAA accessibility onboarding).
