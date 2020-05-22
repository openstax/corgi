import sys
import json
import utils
from pathlib import Path

from lxml import etree
from lxml.builder import ElementMaker, E

from cnxepub.collation import reconstitute
from cnxepub.html_parsers import HTML_DOCUMENT_NAMESPACES
from cnxepub.formatters import DocumentContentFormatter
from cnxepub.models import flatten_to_documents, Document, content_to_etree

def extract_slugs_from_tree(tree, data):
    """Given a tree with slugs create a flattened structure where slug data
    can be retrieved based upon id key
    """
    data.update({
        tree["id"]: tree["slug"]
    })
    if "contents" in tree:
        for node in tree["contents"]:
            extract_slugs_from_tree(node, data)

def extract_slugs_from_binder(binder):
    """Given a binder return a dictionary that allows caller to retrieve
    computed slugs using ident_hash values"""

    # NOTE: The returned tree has 'id' values which are based upon ident_hash
    # fields in the provided model
    tree = utils.model_to_tree(binder)
    slugs = {}
    extract_slugs_from_tree(tree, slugs)
    return slugs

def main():
    """Main function"""
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    out_dir = (in_dir / "disassembled").resolve(strict=True)
    collection_uuid, collection_version = sys.argv[2:4]
    baked_file = (in_dir / "collection.baked.xhtml").resolve(strict=True)
    baked_metdata_file = (in_dir / "collection.baked-metadata.json").resolve(strict=True)

    with open(baked_file, "rb") as file:
        html_root = etree.parse(file)
        binder = reconstitute(file)

        # It's important that we generate slug metadata in parallel with disassemble
        # so that where ident_hash values are based upon potentially randomly
        # generated UUIDs we can still use them as unique keys in JSON outputs
        # without diverging
        slugs = extract_slugs_from_binder(binder)

    with open(baked_metdata_file, "r") as baked_json:
        baked_metadata = json.load(baked_json)
        book_toc_metadata = baked_metadata.get(binder.id)

    nav = html_root.xpath("//xhtml:nav", namespaces=HTML_DOCUMENT_NAMESPACES)[0]

    toc_maker = ElementMaker(namespace=None,
                             nsmap={None: "http://www.w3.org/1999/xhtml"})
    toc = toc_maker.html(E.head(E.title("Table of Contents")),
                         E.body(nav))

    nav_links = toc.xpath("//xhtml:a", namespaces=HTML_DOCUMENT_NAMESPACES)

    for doc in flatten_to_documents(binder):
        id_with_context = f'{collection_uuid}@{collection_version}:{doc.id}'

        module_etree = content_to_etree(doc.content)
        for link in nav_links:
            link_href = link.attrib['href']
            if not link_href.startswith('#'):
                continue
            if module_etree.xpath(f"/xhtml:body/xhtml:div[@id='{link_href[1:]}']", namespaces=HTML_DOCUMENT_NAMESPACES):
                link.attrib['href'] = f'./{id_with_context}.xhtml'

        with open(f"{out_dir / id_with_context}.xhtml", "wb") as out:
            # Inject some styling and JS for QA
            val = str(DocumentContentFormatter(doc))
            val = val.replace('<body', u'''
                <head>
                    <style>
                        /* Linking to a specific element should highlight the element */
                        :target {
                            background-color: #ffffcc;
                            border: 1px dotted #000000;

                            animation-name: cssAnimation;
                            animation-duration: 10s;
                            animation-timing-function: ease-out;
                            animation-delay: 0s;
                            animation-fill-mode: forwards;
                        }
                        @keyframes cssAnimation {
                            to {
                                background-color: initial;
                                border: initial;
                            }
                        }

                        /* Style footnotes so that they stand out */
                        [role="doc-footnote"] { background-color: #ffcccc; border: 1px dashed #ff0000; }
                        [role="doc-footnote"]:before { content: "FOOTNOTE " ; }
                        
                        /* Show a permalink when hovering over a heading or paragraph */
                        *:not(:hover) > a.-permalinker { display: none; }
                        * > a.-permalinker {
                            margin-left: .1rem;
                            font-weight: bold;
                            text-decoration: none;
                        }
                    </style>
                </head>
                <body''')
            val = val.replace('</body>', u'''
                <script>//<![CDATA[
                
                    const pilcrow = '¶'

                    function addPermalink(parent, id) {
                        const link = window.document.createElement('a')
                        link.classList.add('-permalinker')
                        link.setAttribute('href', `#${id}`)
                        link.textContent = pilcrow
                        parent.appendChild(link)
                    }

                    const paragraphs = Array.from(document.querySelectorAll('p[id]'))
                    paragraphs.forEach(p => addPermalink(p, p.getAttribute('id')) )

                    const headings = Array.from(document.querySelectorAll('*[id] > h1, *[id] > h2, *[id] > h3, *[id] > h4, *[id] > h5, *[id] > h6'))
                    headings.forEach(h => addPermalink(h, h.parentElement.getAttribute('id')) )

                // ]]></script>
                </body>''')
            out.write(bytes(val.encode('utf-8')))

        with open(f"{out_dir / id_with_context}-metadata.json", "w") as json_out:
            # Incorporate metadata from disassemble step while setting defaults
            # for cases like composite pages which may not have metadata from
            # previous stages
            json_metadata = {
                "slug": slugs.get(doc.ident_hash),
                "title": doc.metadata.get("title"),
                "abstract": None
            }

            # Add / override metadata from baking if available
            json_metadata.update(baked_metadata.get(doc.ident_hash, {}))

            json.dump(
                json_metadata,
                json_out
            )

    with open(f"{out_dir}/collection.toc.xhtml", "wb") as out:
        out.write(etree.tostring(toc, encoding="utf8", pretty_print=True))

    with open(f"{out_dir}/collection.toc-metadata.json", "w") as toc_json:
        json.dump(book_toc_metadata, toc_json)

if __name__ == "__main__":
    main()
