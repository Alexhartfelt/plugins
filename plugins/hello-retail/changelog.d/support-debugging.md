### Added

- `support-debugging` debugs a Hello Retail support ticket and answers it from evidence. It gates
  the ticket first — confirming the website and the feature, which arrive unverified and are
  routinely wrong — then reads the live configuration, reproduces the symptom on the storefront,
  and proposes only the fix the evidence supports, cited to the config, the reproduction or the
  knowledge base. Causes outside what the MCP can reach are handed back in the first line rather
  than investigated around.
