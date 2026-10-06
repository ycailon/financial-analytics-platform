# Engineering decisions

## Use standardized source APIs instead of scraped financial websites

The project uses SEC and BLS public APIs so the source and meaning of the data are explicit. It also avoids building a portfolio project around a third-party site's HTML layout.

## Keep metric mapping configurable

A company can report a comparable business concept under different standard US-GAAP tags. The canonical metric stays stable while candidate SEC concepts are configured in YAML.

## Keep raw facts long; create wide marts later

The warehouse stores financial facts in a long fact table. This is easier to audit and extend. A SQL mart pivots the metrics only for analysis and dashboard use.

## Keep source evidence

The source XBRL concept, filing date and accession number are kept with every selected fact. A dashboard number should be traceable back to the filing choice that produced it.

## SQLite by default

This is a portfolio project, so I wanted one command to work without asking someone to install a database server. SQLite keeps the demo simple while still letting the project demonstrate schema design, keys, indexes, CTEs, window functions, views and analytical SQL.

## Do not imply macro data caused company performance

The economic-context mart lines company fiscal years up with calendar-year CPI and unemployment averages. It is for context and comparison, not causal inference.
