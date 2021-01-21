import re


dict_pattern = re.compile(r'{.+}', flags=re.DOTALL)
space_curly_braces = re.compile(r'[\n {}]')
split_pattern = re.compile(r'[:,]')

PAGINATION_URL = '?page=%number%'
PAGES_SPAN_KEY = 'pagesSpan'

# gets the pagination number
def pagination_count(s):
    dict_list = dict_pattern.findall(s)

    for each in dict_list:
        if PAGINATION_URL in each:
            dict_str = each
            break

    try:
        dic = space_curly_braces.sub('', dict_str)
        dic = split_pattern.split(dic)
    except:
        return

    pages_span = None

    for i in range(len(dic)):
        if dic[i] == PAGES_SPAN_KEY:
            pages_span = int(dic[i + 1])

    if pages_span:
        return pages_span
    else:
        return
