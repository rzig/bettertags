# Bettertags

`bettertags` is an enhanced version of the [mkdocs-material built-in tags plugin](https://squidfunk.github.io/mkdocs-material/plugins/tags) with FREE improved versions of the following `mkdocs-material` insiders features:

- `tags_extra_files`
- `tags_allowed`

This plugin is originally based on the MIT-licensed source from `mkdocs-material`, but many parts have been heavily refactored/rewritten.

## Installation and usage

1. Run `pip install bettertags`
2. Replace the `tags` configruation option of your `mkdocs.yml` with `bettertags`
3. Add the following to the `plugins` section of `mkdocs.yml`:

```
- tags:
   tags: false
```

So, if your `mkdocs.yml` previously looked like this:

```
site_name: Dr. Everitt's Neighborhood
site_url: https://wiki.hkn.illinois.edu
theme:
  name: material
  palette:
    primary: custom
    accent: custom
    typeset: custom
  features:
    - navigation.tabs
extra_css:
  - styles/theme.css
plugins:
  - search
  - tags:
      tags_file: index.md
```

now it should look like this:

```
site_name: Dr. Everitt's Neighborhood
site_url: https://wiki.hkn.illinois.edu
theme:
  name: material
  palette:
    primary: custom
    accent: custom
    typeset: custom
  features:
    - navigation.tabs
extra_css:
  - styles/theme.css
plugins:
  - search
  - tags:
      tags: false
  - bettertags:
      tags_file: index.md
```

That's it! You can use any of the above insiders features without any additional work.

## `tags_extra_files`

Use this option to add additional tag lists to your wiki:

```
plugins:
  - bettertags:
      tags_extra_files:
        extra-1.md: [allowed-tag-1, allowed-tag-2, ...]
        extra-2.md: "*subfolder"
        extra-3.md: "*"
        "folder/extra-4.md":
            - rule: "*subfolder"
            - priority: 3
```

Each tag index can have one of the following rules:

- `[allowed-tag-1, ...]`: only include tags from the given list
- `*subfolder`: only include tags and pages from files contained within the same parent folder as this index
- `*`: include all tags and pages

An index may also have an associated priority. By default, all extra indexes have priority `0`, and the primary index (from `tags_file` option) has priority `1`. When a tag on a wiki page is linked back to a tag index, it is linked to the index with the highest priority that contains the page. By default, this means a tag will always link back to the primary tags index. In the above example, only pages in `folder/` will have tags linking to `folder/extra-4.md`. It is considered _undefined behavior_ to have multiple indexes that _tie_ for having the _highest priority_ for a given page/tag pair.

`tags_extra_files` can also be replaced with `indexes` for improved clarity.

## `allowed_tags`

This works just like the [`allowed-tags`](https://squidfunk.github.io/mkdocs-material/plugins/tags/#config.tags_allowed) option from `mkdocs-material`, I haven't added anything to it.
