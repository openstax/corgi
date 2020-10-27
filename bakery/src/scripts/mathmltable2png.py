from lxml import etree
import os
import io
import sys
import requests
import base64
import hashlib
import struct

DENSITY_DPI = 900


def force_math_namespace_only(doc):
    # http://wiki.tei-c.org/index.php/Remove-Namespaces.xsl
    xslt = u'''<xsl:stylesheet
      version="1.0"
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns="http://www.w3.org/1998/Math/MathML">
    <xsl:output method="xml" indent="no"/>

    <xsl:template match="/|comment()|processing-instruction()">
        <xsl:copy>
          <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="*">
        <xsl:element name="{local-name()}">
          <xsl:apply-templates select="@*|node()"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="@*">
        <xsl:attribute name="{local-name()}">
          <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    </xsl:stylesheet>
    '''
    xslt_doc = etree.parse(io.StringIO(xslt))
    transform = etree.XSLT(xslt_doc)
    doc = transform(doc)
    return doc


def strip_mathjax_container(svg):
    xslt = u'''<xsl:stylesheet
      version="1.0"
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns="http://www.w3.org/1998/Math/MathML">
    <xsl:output method="xml" indent="no"/>

    <xsl:template match="mjx-container">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

    </xsl:stylesheet>
    '''
    xslt_doc = etree.parse(io.StringIO(xslt))
    svg_xml = etree.parse(io.StringIO(svg))
    transform = etree.XSLT(xslt_doc)
    svg_xml = transform(svg_xml)
    bytes_svg = etree.tostring(svg_xml, with_tail=False)
    pure_svg = str(bytes_svg, 'utf-8')
    return pure_svg


def get_png_dimensions(png_bytes):
    check = struct.unpack('>i', png_bytes[4:8])[0]
    if check != 0x0d0a1a0a:
        return 0, 0
    width, height = struct.unpack('>ii', png_bytes[16:24])
    return width, height


def mathml2svg_jsonrpc(equation):
    url = "http://localhost:3000/jsonrpc"
    payload = {
        "method": "mathml2svg",
        "params": [equation],
        "jsonrpc": "2.0",
        "id": 0,
    }

    response = requests.post(url, json=payload).json()

    if not 'result' in response:
        # something went terrible wrong with calling the jsonrpc server and running the command
        print('No result in calling mml2svg jayson/json-rpc server!')
        sys.exit(1)
        return '', ''
    else:
        svg = response['result'][0]
        mathspeak = response['result'][1]
        if len(svg) > 0:
            svg = strip_mathjax_container(svg)
        return svg, mathspeak


def svg2png_jsonrpc(svg):
    url = "http://localhost:3000/jsonrpc"
    payload = {
        "method": "svg2png",
        "params": [svg],
        "jsonrpc": "2.0",
        "id": 0,
    }

    response = requests.post(url, json=payload).json()

    if not 'result' in response:
        # something went terrible wrong with calling the jsonrpc server and running the command
        print('No result in calling mml2svg jayson/json-rpc server!')
        sys.exit(1)
        return ''
    else:
        png_base64 = response['result']
        png_bytes = b''
        if len(png_base64) > 0:
            png_bytes = base64.b64decode(png_base64)
        return png_bytes

# argument 1: xhtml file with mathml mtable equations
# argument 2: resource folder
def main():
    if sys.version_info[0] < 3:
        raise Exception("Must be using Python 3")
    f = etree.parse(sys.argv[1])
    ns = {"h": "http://www.w3.org/1999/xhtml",
          "m": "http://www.w3.org/1998/Math/MathML"}

    for r in f.xpath('//h:math[descendant::h:mtable]|//m:math[descendant::m:mtable]', namespaces=ns):
        math_etree = force_math_namespace_only(r)
        bytes_equation = etree.tostring(
            math_etree, with_tail=False, inclusive_ns_prefixes=None)
        # convert bytes string from lxml to utf-8
        equation = str(bytes_equation, 'utf-8')
        svg, mathspeak = mathml2svg_jsonrpc(equation)

        # do not replace if conversion failed
        if svg:
            png = svg2png_jsonrpc(svg)
            if png:
                png_width, png_height = get_png_dimensions(png)
                if png_width > 0 and png_height > 0:
                    sha1 = hashlib.sha1(png)
                    png_filename = os.path.join(sys.argv[2], sha1.hexdigest())
                    relative_resource_filename = '../resources/' + os.path.basename(png_filename)
                    png_file = open(png_filename, 'wb')
                    png_file.write(png)
                    png_file.close()
                    display_width = round(png_width / (DENSITY_DPI / 75 - 1))
                    display_height = round(png_height / (DENSITY_DPI / 75 - 1))
                    img_xhtml = '<img src="{}" alt="{}" width="{}" height="{}" />'.format(
                        relative_resource_filename, mathspeak, display_width, display_height)
                    img_formatted = etree.fromstring(img_xhtml)
                    # replace MathML with img tag
                    r.getparent().replace(r, img_formatted)
                else:
                    raise Exception('Failed to get PNG image dimensions of equation' + equation)
            else:
                raise Exception('Failed to generate PNG from SVG of equation: ' + equation)
        else:
            raise Exception('Failed to generate SVG from MathML of equation: ' + equation)

    print(etree.tostring(f, pretty_print=False).decode('utf-8'))

if __name__ == "__main__":
    main()
