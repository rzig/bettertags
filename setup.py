from setuptools import setup, find_packages


setup(
    name="bettertags",
    version="1.1.0",
    author="ryan",
    author_email="ryan@ziegler.lol",
    url="https://github.com/rzig/bettertags",
    install_requires=["markdown", "mkdocs"],
    description="mkdocs-material tag plugin with FREE enhanced versions of all insiders features",
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        "mkdocs.plugins": [
            "bettertags = bettertags.plugin:TagsPlugin",
        ]
    },
)
