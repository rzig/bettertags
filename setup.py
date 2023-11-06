from setuptools import setup, find_packages


setup(
    name="bettertags",
    version="1.0.2",
    author="ryan",
    author_email="ryan@ziegler.lol",
    url="https://github.com/rzig/bettertags",
    install_requires=["markdown", "mkdocs"],
    description="mkdocs-material tag plugin with free enhanced versions of some insiders features",
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        "mkdocs.plugins": [
            "bettertags = bettertags.plugin:TagsPlugin",
        ]
    },
)
