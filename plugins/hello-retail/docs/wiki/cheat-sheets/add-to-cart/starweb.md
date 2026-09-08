# Add-to-Cart — Starweb
Starweb exposes a global `quickShop` module that handles add-to-cart. After HR renders a product card, just init it.

For platform overview see [../README.md](../README.md).

---

### _Initialize quickShop for add-to-cart_

Single-line init — call after HR renders results / recoms.

```javascript
quickShop.init()
```

**When to call it:**

- After Search overlay activates.
- After Recommendation widget mounts.
- After Pages renders.

If `quickShop` is undefined when called, the customer either isn't on Starweb or the platform's JS hasn't loaded yet — wrap in a polling helper (see [../pages/general.md](../pages/general.md) → "Look for an element repeatedly until found") to wait for it.

---

## Timeline
- 2026-05-21: Starweb quickShop init documented from the team's Starweb cheat sheet.
