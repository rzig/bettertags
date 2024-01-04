# Bettertags

`bettertags` is an enhanced version of the [`mkdocs-material` built-in tags plugin](https://squidfunk.github.io/mkdocs-material/plugins/tags) with FREE versions of all Insiders-only tags features, and some minor improvements.

This plugin is originally based on the MIT-licensed source from `mkdocs-material`, but many parts have been heavily refactored/rewritten (and weren't written without any knowledge of the Material Insiders source). If you have suggestions of extra enhancements, please open an issue.

## Installation and usage

1. Run `pip install bettertags`
2. Replace the `tags` configruation option of your `mkdocs.yml` with `bettertags`
3. If you use Material-provided functions for `tags_compare` or `tags_pages_compare`, replace `material.plugins.tags` with `bettertags`

You can now use any insiders-only features [described in the Material docs](https://squidfunk.github.io/mkdocs-material/plugins/tags). I've also added a few features to `tags_extra_files`, described below.

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

Each tag index can have one of the following types of rules:

- `[allowed-tag-1, ...]`: only include tags from the given list
- `*subfolder`: only include tags and pages from files contained within the same parent folder (or any descendants) as this index
- `*`: include all tags and pages

An index may also have an associated priority. By default, all extra indexes have priority `0`, and the primary index (from `tags_file` option) has priority `1`. When a tag on a wiki page is linked back to a tag index, it is linked to the index with the highest priority that contains the page. By default, this means a tag will always link back to the primary tags index. In the above example, pages in `folder/` will have tags linking to `folder/extra-4.md`, since `folder/` has a priority `3 > 1`. If a tag is shown in two indices with the same priority, it will link back to the index with the longest shared prefix between its file path and the path of the file containing the tag. That is, if indices `/tags.md` and `/folder/tags.md` both have priority `1`, a tag in `/folder/subfolder/file.md` will link to `/folder/tags.md`. It is considered _undefined behavior_ to have multiple indexes that _tie_ for having the _highest priority and longest shared prefix_ for a given page/tag pair.

`tags_extra_files` can also be replaced with `indexes` in your config for improved clarity.
