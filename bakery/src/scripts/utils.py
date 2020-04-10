from cnxepub.models import TRANSLUCENT_BINDER_ID, TranslucentBinder
from cnxcommon.urlslug import generate_slug

# Based upon amend_tree_with_slugs from cnx-publishing
# (https://github.com/openstax/cnx-publishing/blob/master/cnxpublishing/utils.py#L64)
def amend_tree_with_slugs(tree, title_seq=[]):
    """Recursively walk through tree and add slug fields"""
    title_seq = title_seq + [tree['title']]
    tree['slug'] = generate_slug(*title_seq)
    if 'contents' in tree:
        for node in tree['contents']:
            amend_tree_with_slugs(node, title_seq)

# Based upon model_to_tree from cnx-epub
# (https://github.com/openstax/cnx-epub/blob/master/cnxepub/models.py#L108)
def model_to_tree(model, title=None, lucent_id=TRANSLUCENT_BINDER_ID):
    """Given an model, build the tree::
        {'id': <id>|'subcol', 'title': <title>, 'contents': [<tree>, ...]}
    """
    id = model.ident_hash
    if id is None and isinstance(model, TranslucentBinder):
        id = lucent_id
    md = model.metadata
    title = title is not None and title or md.get('title')
    tree = {'id': id, 'title': title}
    if hasattr(model, '__iter__'):
        contents = tree['contents'] = []
        for node in model:
            item = model_to_tree(node, model.get_title_for_node(node),
                                 lucent_id=lucent_id)
            contents.append(item)
    amend_tree_with_slugs(tree)
    return tree

def parse_uri(uri):
    if not uri.startswith('col', 0, 3): return None
    legacy_id, legacy_version = uri.split('@')
    return legacy_id, legacy_version

