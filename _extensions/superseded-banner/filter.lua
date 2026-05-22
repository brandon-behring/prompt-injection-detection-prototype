-- Quarto Lua filter: inject a callout-warning banner at the top of any ADR
-- whose frontmatter `superseded_by:` is non-empty. Source ADR files remain
-- immutable per the ADR-073 immutability rule; the banner only appears in
-- rendered HTML.
--
-- Wired into _quarto.yml `filters:` per ADR-081 narrow-relaxation chain
-- (sixth axis: rendering-only supersession banner) + the v1.3.2 P2-1 fix
-- from AUDIT_CLAUDE_2026-05-22. Source: F1 lock (Lua filter native AST
-- manipulation) from /exploring-options 2026-05-22.
--
-- Triggers when BOTH of the following hold:
-- 1. The document's frontmatter has an `adr_id:` field (identifies ADR docs).
-- 2. The frontmatter `superseded_by:` field is present + non-empty.

local function stringify(node)
  return pandoc.utils.stringify(node):gsub("^%s+", ""):gsub("%s+$", "")
end

-- Extract a flat list of trimmed string IDs from a frontmatter
-- field whose type may be MetaList / MetaInlines / MetaString.
local function extract_id_list(field)
  local ids = {}
  if field == nil then
    return ids
  end
  if type(field) == "table" and field.t == "MetaList" then
    for _, entry in ipairs(field) do
      local s = stringify(entry)
      if s ~= "" then
        table.insert(ids, s)
      end
    end
  else
    local s = stringify(field)
    if s ~= "" then
      table.insert(ids, s)
    end
  end
  return ids
end

-- Pandoc filter entry point: walks the Pandoc document AST.
function Pandoc(doc)
  local meta = doc.meta or {}
  local adr_id = meta.adr_id
  local superseded_by = meta.superseded_by

  -- Gate 1: document must be an ADR (frontmatter has `adr_id:`).
  if adr_id == nil then
    return nil
  end

  -- Gate 2: `superseded_by:` must be present + non-empty.
  local ids = extract_id_list(superseded_by)
  if #ids == 0 then
    return nil
  end

  -- Build a markdown-formatted list of bold-text "ADR-NNN" labels.
  local items = {}
  for _, id_str in ipairs(ids) do
    -- Pad to 3 digits if shorter (the YAML may store "80" or "081"; the
    -- canonical form is 3-digit per ADR-077 octal-quoting discipline).
    local padded = id_str
    while #padded < 3 do
      padded = "0" .. padded
    end
    table.insert(items, "**ADR-" .. padded .. "**")
  end
  local list_md = table.concat(items, ", ")

  local banner_md = string.format(
    "**Superseded on one or more axes** by %s. " ..
    "The body below retains its original prose per the " ..
    "[ADR-073 immutability rule](ADR-073-adr-immutability-rule-consolidated-re-statement.html); " ..
    "the corrected position lives in the superseding ADR. " ..
    "See the [Decisions index](README.html) to navigate.",
    list_md
  )

  -- Parse the markdown into Pandoc blocks.
  local banner_blocks = pandoc.read(banner_md, "markdown").blocks

  -- Wrap in a callout-warning Div.
  local callout = pandoc.Div(
    banner_blocks,
    pandoc.Attr("", {"callout-warning"}, {})
  )

  -- Prepend to the document body.
  table.insert(doc.blocks, 1, callout)

  return doc
end
