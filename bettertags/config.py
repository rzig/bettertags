from functools import partial
from markdown.extensions.toc import slugify
from mkdocs.config.config_options import Optional, Type
from mkdocs.config.base import Config

from . import casefold


class TagsConfig(Config):
    enabled = Type(bool, default=True)

    tags = Type(bool, default=True)
    tags_file = Optional(Type(str))
    tags_extra_files = Optional(Type(dict))
    indices = Optional(Type(dict))
    tags_allowed = Optional(Type(list))
