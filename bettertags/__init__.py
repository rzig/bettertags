def casefold(tag: str):
    return tag.casefold()

def page_title(page):
    return page.meta.get("title", page.title)

def page_url(page):
    return page.url