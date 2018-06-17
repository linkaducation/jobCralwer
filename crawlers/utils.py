import itertools
from lxml import etree


def get_document(html):
    """
    将HTML转化为etree.ElementTree结构
    :param html:
    :return:
    """
    p = etree.HTMLParser(encoding='utf-8')
    document = etree.fromstring(html, p)
    return document


def get_simple_dom(dom, xpath, default=None):
    """
    获取dom中xpath指定路径的取到的第一个值
    :param dom:
    :param xpath:
    :param default:
    :return:
    """
    _ = dom.xpath(xpath)
    if len(_) > 0:
        return _[0]
    return default


def get_richtext_dom(node):
    """
    将node这个节点去掉标签等HTML元素，返回标签中的值
    :param node:
    :return:
    """
    if node is not None:
        parts = (
                [node.text] + list(itertools.chain(*([get_richtext_dom(c)
                                                      if c.getchildren() else ((c.text or '') + (c.tail or ''))] for c
                                                     in node.getchildren()))) + [node.tail]
        )
        return '\n'.join([item.strip() for item in filter(None, parts) if item.strip()])
    return ''


def remove_tags(text):
    """
    删除文本中的tag节点
    :param text:
    :return:
    """
    document = etree.fromstring(text)
    return document.text_content()


def get_richtext(dom, xpath):
    """
    根据xpath获取dom节点的值
    :param dom:
    :param xpath:
    :return:
    """
    _ = dom.xpath(xpath)
    if len(_) > 0:
        result = remove_tags(etree.tostring(_[0])).strip()
    else:
        result = ''
    return result


def get_html_by_document(document):
    """
    将document转化为str
    :param document:
    :return:
    """
    return etree.tostring(document)
