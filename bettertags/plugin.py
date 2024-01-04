import logging
import sys
from collections import defaultdict
from markdown.extensions.toc import slugify
from mkdocs import utils
from mkdocs.plugins import BasePlugin
from . import casefold
from .config import TagsConfig

DEFAULT_PRIORITY = 0


class MaterialTagsShim(BasePlugin[TagsConfig]):
    def __init__(self):
        pass


def argmax(f, it):
    cur_max = None
    set_by = None
    for x in it:
        f_x = f(x)
        if cur_max == None or f_x > cur_max:
            cur_max = f_x
            set_by = x
    return set_by

def lcp(x, y):
    l = 0
    for i in range(min(len(x), len(y))):
        if x[i] == y[i]:
            l += 1
        else:
            break
    return l


class TagsPlugin(BasePlugin[TagsConfig]):
    def on_config(self, config):
        if not self._is_enabled():
            return

        self.tags_map = config.extra.get("tags")

        toc = {"slugify": slugify, "separator": "-"}
        if "toc" in config.mdx_configs:
            toc = {**toc, **config.mdx_configs["toc"]}

        toc["slugify"] = self.config.get("tags_slugify", toc["slugify"])
        toc["separator"] = self.config.get("tags_slugify_separator", toc["separator"])

        iden = lambda x: x
        self.tag_sort_key = self.config.get("tags_compare")
        self.tags_reorder = (
            reversed if self.config.get("tags_compare_reverse", False) else iden
        )
        self.page_sort_key = self.config.get("tags_pages_compare")
        self.pages_reorder = (
            reversed if self.config.get("tags_pages_compare_reverse", False) else iden
        )

        self.slugify = lambda value: (toc["slugify"](str(value), toc["separator"]))

    def on_nav(self, nav, config, files):
        if not self._is_enabled():
            return

        tags_extra_files = self.config.get("tags_extra_files", dict())
        if tags_extra_files == None:
            tags_extra_files = dict()
        indexes = self.config.get("indexes", dict())
        if indexes == None:
            indexes = dict()
        self.index_rules, self.index_priority = self._extract_rules_and_priority(
            {
                **tags_extra_files,  # compat with bad naming by material
                **indexes,
            }
        )
        if self.config.tags_file:
            self.index_rules[self.config.tags_file] = "*"
            self.index_priority[self.config.tags_file] = DEFAULT_PRIORITY + 1

        load_file = lambda f: self._get_tags_file(files, f)

        self.index_filenames = set(self.index_rules.keys())
        self.index_files = dict(
            zip(self.index_filenames, map(load_file, self.index_filenames))
        )
        self.tags_in_index = {f: defaultdict(list) for f in self.index_filenames}
        self.indexes_with_tag = defaultdict(set)

        self.allowed_tags = self.config.get("tags_allowed", None)

    def on_page_markdown(self, markdown, page, config, files):
        if not self._is_enabled() or page.file.inclusion.is_excluded():
            return

        if page.file.src_uri in self.index_files:
            return self._render_tag_index(
                page.file, self.tags_in_index[page.file.src_uri], markdown
            )

        for index_page in self.index_files:
            if self._page_in_index(index_page, page):
                for tag in page.meta.get("tags", []):
                    self._validate_tag(page.file.src_uri, tag)
                    if self._tag_allowed_in_index(index_page, tag):
                        self.tags_in_index[index_page][tag].append(page)
                        self.indexes_with_tag[tag].add(index_page)

    def on_page_context(self, context, page, config, nav):
        if not self._is_enabled():
            return

        if "tags" in page.meta:
            # Bypass check for material/tags at
            # https://github.com/squidfunk/mkdocs-material/blob/master/src/templates/partials/content.html#L24
            context["config"]["plugins"]["material/tags"] = MaterialTagsShim()
            context["tags"] = [self._render_tag(page, tag) for tag in page.meta["tags"]]

    # -------------------------------------------------------------------------

    def _get_tags_file(self, files, path):
        file = files.get_file_from_path(path)
        if not file:
            log.error(f"Tags file '{path}' does not exist.")
            sys.exit(1)

        files.append(file)
        return file

    def _render_tag_index(self, index_file, tags, markdown):
        if not "[TAGS]" in markdown:
            markdown += "\n[TAGS]"

        return markdown.replace(
            "[TAGS]",
            "\n".join(
                [
                    self._render_tag_links(index_file, *args)
                    for args in self.tags_reorder(
                        self._sort_if_possible(
                            self.tag_sort_key, tags.items(), by=lambda tag: tag[0]
                        )
                    )  # sort by tag name
                ]
            ),
        )
        return markdown

    def _render_tag_links(self, index_file, tag, pages):
        classes = ["md-tag"]
        if isinstance(self.tags_map, dict):
            classes.append("md-tag-icon")
            type = self.tags_map.get(tag)
            if type:
                classes.append(f"md-tag--{type}")

        classes = " ".join(classes)
        # tag slugify separator might be different than mdx separator
        # so we need to manually specify the h2 id
        content = [
            f'<h2 id="{self.slugify(tag)}"><span class="{classes}">{tag}</span></h2>',
            "",
        ]
        for page in self.pages_reorder(
            self._sort_if_possible(self.page_sort_key, pages)
        ):
            url = utils.get_relative_url(page.file.src_uri, index_file.src_uri)
            title = page.meta.get("title", page.title)
            content.append(f"- [{title}]({url})")

        return "\n".join(content)

    def _render_tag(self, page, tag):
        best_index = argmax(
            lambda p: (self.index_priority[p], lcp(p, page.file.src_uri)), self.indexes_with_tag[tag]
        )
        tag_type = self.tags_map.get(tag) if self.tags_map else None
        if not best_index:
            return dict(name=tag, type=tag_type)
        else:
            best_index_file = self.index_files[best_index]
            url = f"{best_index_file.url}#{self.slugify(tag)}"
            return dict(name=tag, type=tag_type, url=url)

    def _is_enabled(self):
        return self.config.enabled and self.config.tags

    def _page_in_index(self, index, page):
        index_rule = self.index_rules[index]
        if index_rule == "*" or isinstance(index_rule, list):
            return True
        elif index_rule == "*subfolder":
            index_folder = self._parent_folder_path(self.index_files[index].src_uri)
            return page.file.src_uri.startswith(index_folder)
        else:
            return False

    def _tag_allowed_in_index(self, index, tag):
        index_rule = self.index_rules[index]
        if not isinstance(index_rule, list):
            return True
        else:
            return tag in index_rule

    def _parent_folder_path(self, file_path):
        return "/".join(file_path.split("/")[:-1])

    def _extract_rules_and_priority(self, index_files):
        rules = dict()
        priorities = dict()
        for index_file in index_files:
            provided_spec = index_files[index_file]
            if isinstance(provided_spec, dict):
                if not ("rule" in provided_spec and "priority" in provided_spec):
                    log.error("Expected 'rule' and 'priority' in specification.")
                    sys.exit(1)
                rules[index_file] = provided_spec["rule"]
                priorities[index_file] = int(provided_spec["priority"])
            else:
                rules[index_file] = provided_spec
                priorities[index_file] = DEFAULT_PRIORITY
        self._validate_index_rules(rules)
        return rules, priorities

    def _validate_index_rules(self, index_rules):
        for index in index_rules:
            if index_rules[index] not in {"*", "*subfolder"} and not isinstance(
                index_rules[index], list
            ):
                log.error(f"Tags index {index} has invalid rule {index_rules[index]}")
                sys.exit(1)

    def _validate_tag(self, src_uri, tag):
        if self.allowed_tags and tag not in self.allowed_tags:
            log.error(f"Tag '{tag}' is not allowed, found at file {src_uri}")
            sys.exit(1)

    def _sort_if_possible(self, data_key, data, by=lambda x: x):
        if data_key is not None:
            return sorted(data, key=lambda data: data_key(by(data)))
        else:
            return data


log = logging.getLogger("mkdocs.material.tags")
