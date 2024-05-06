from typing import List, Optional

from lxml import etree

from app.core.errors import CustomBaseError


class XMLParseError(CustomBaseError):
    def __init__(self, msg: str) -> None:
        super().__init__(f"{self.__class__.__name__}: {msg}")


class XPathError(XMLParseError):
    def __init__(self, xpath: str) -> None:
        super().__init__(f"XPath did not match any elements '{xpath}'")


def xpath_some(tree: etree.ElementBase, xpath: str) -> List[etree.ElementBase]:
    """Use this when you expect to get at least one result from an xpath"""
    ret = tree.xpath(xpath)
    if len(ret) == 0:
        raise XPathError(xpath)
    return ret


def xpath1(tree: etree.ElementBase, xpath: str) -> Optional[etree.ElementBase]:
    """Use this when you expect to get the first result from an xpath"""
    try:
        return tree.xpath(xpath)[0]
    except IndexError as ie:
        raise XPathError(xpath) from ie


def get_attr(element: etree.ElementBase, key: str) -> str:
    """Use this when you expect to get a value for an attribute"""
    ret = element.attrib.get(key, None)
    if ret is None:
        raise XMLParseError(f"Missing attribute '{key}' on '{element.tag}'")
    return ret


def parse_xml_doc(xml_doc: str):
    try:
        return etree.fromstring(xml_doc, parser=None)
    except ValueError:  # pragma: no cover
        # If the xml document has an encoding declaration
        # `text` in GitHub graphql is "UTF8 text data[...]"
        return etree.fromstring(xml_doc.encode("utf-8"), parser=None)
