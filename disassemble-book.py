import sys
import json
from pathlib import Path
from cnxepub.collation import reconstitute
from cnxepub.formatters import DocumentContentFormatter
from cnxepub.models import flatten_to, Document, model_to_tree
from cnxcommon.urlslug import generate_slug


# Based upon amend_tree_with_slugs from cnx-publishing
# (https://github.com/openstax/cnx-publishing/blob/master/cnxpublishing/utils.py#L64)
def amend_tree_with_slugs(tree, title_seq=[]):
    """Recurisvely walk through tree and add slug fields"""
    title_seq = title_seq + [tree['title']]
    tree['slug'] = generate_slug(*title_seq)
    if 'contents' in tree:
        for node in tree['contents']:
            amend_tree_with_slugs(node, title_seq)

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
    tree = model_to_tree(binder)
    amend_tree_with_slugs(tree)
    slugs = {}
    extract_slugs_from_tree(tree, slugs)
    return slugs


in_dir = Path(sys.argv[1]).resolve(strict=True)
out_dir = (in_dir / "disassembled").resolve(strict=True)
# raw_dir = (in_dir / "raw").resolve(strict=True)
baked_file = (in_dir / "collection.baked.xhtml").resolve(strict=True)
baked_metdata_file = (in_dir / "collection.baked-metadata.json").resolve(strict=True)

with open(baked_file, "rb") as file:
    binder = reconstitute(file)

    # It's important that we generate slug metadata in parallel with disassemble
    # so that where ident_hash values are based upon potentially randomly
    # generated UUIDs we can still use them as unique keys in JSON outputs
    # without diverging
    slugs = extract_slugs_from_binder(binder)

with open(baked_metdata_file, "r") as baked_json:
    baked_metadata = json.load(baked_json)

for doc in flatten_to(binder, lambda d: isinstance(d, Document)):
    with open(f"{out_dir / doc.ident_hash}.xhtml", "wb") as out:
        # TODO: Copy resources from module to here (from raw_dir?)
        out.write(bytes(DocumentContentFormatter(doc)))
    with open(f"{out_dir / doc.ident_hash}-metadata.json", "w") as json_out:
        # Incorporate metadata from disassemble step
        json_metadata = {
            "slug": slugs.get(doc.ident_hash),
            "title": doc.metadata.get("title")
        }

        # Add additional metadata from baking if available
        json_metadata.update(baked_metadata.get(doc.ident_hash, {}))

        json.dump(
            json_metadata,
            json_out
        )

# Publishing calls these and these are needed to generate json,
# but they are harder to reach (cnx-publishing -> cnx-common)
#
# https://github.com/openstax/cnx-publishing/blob/master/cnxpublishing/bake.py#L92
# tree = model_to_tree(binder)
# amend_tree_with_slugs(tree)
