import hashlib
import magic
from cnxepub.models import TRANSLUCENT_BINDER_ID, TranslucentBinder
from cnxcommon.urlslug import generate_slug

# same as boto3 default chunk size. Don't modify.
BUF_SIZE = 8 * 1024 * 1024


# https://stackoverflow.com/a/22058673/756056
def get_checksums(filename):
    """ generate SHA1 and S3 MD5 etag checksums from file """
    sha1 = hashlib.sha1()
    md5s = []
    try:
        with open(filename, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
                md5s.append(hashlib.md5(data))
        # chunked calculation for AWS S3 MD5 etag
        # https://stackoverflow.com/a/43819225/756056
        #
        # AWS needs the MD5 quoted inside the string json value.
        # Despite looking like a mistake, this is correct behavior.
        if len(md5s) < 1:
            s3_md5 = '"{}"'.format(hashlib.md5().hexdigest())
        elif len(md5s) == 1:
            s3_md5 = '"{}"'.format(md5s[0].hexdigest())
        else:
            digests = b''.join(m.digest() for m in md5s)
            digests_md5 = hashlib.md5(digests)
            s3_md5 = '"{}-{}"'.format(digests_md5.hexdigest(), len(md5s))
        return sha1.hexdigest(), s3_md5
    except IOError:     # file does not exist
        return None, None


def get_mime_type(filename):
    """ get MIME type of file with libmagic """
    mime_type = ''
    try:
        mime_type = magic.from_file(filename, mime=True)
    finally:
        return mime_type


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
    if not uri.startswith('col', 0, 3):
        return None
    legacy_id, legacy_version = uri.split('@')
    return legacy_id, legacy_version
