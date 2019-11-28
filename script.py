#!/usr/bin/env python3
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
import argparse
import json
import lxml.etree as et

NS = {"gmx": "http://www.isotc211.org/2005/gmx", "gmd": "http://www.isotc211.org/2005/gmd","csw": "http://www.opengis.net/cat/csw/2.0.2","gco": "http://www.isotc211.org/2005/gco","gml": "http://www.opengis.net/gml","gmx": "http://www.isotc211.org/2005/gmx","gsr": "http://www.isotc211.org/2005/gsr","gts": "http://www.isotc211.org/2005/gts","srv": "http://www.isotc211.org/2005/srv","xlink":"http://www.w3.org/1999/xlink", "geonet":"http://www.fao.org/geonetwork" }

SERVICE_TYPES = {
    "OGC:CSW": "CSW",
    "OGC:WMS": "WMS",
    "OGC:WMTS": "WMTS",
    "OGC:WFS": "WFS",
    "OGC:WCS": "WCS",
    "OGC:SOS": "SOS",
    "INSPIRE Atom": "ATOM"
}

XPATH_METADATA="/gmd:MD_Metadata"
XPATH_SERVICE_ID=f"{XPATH_METADATA}/gmd:identificationInfo/srv:SV_ServiceIdentification"

def main(md_file_path, inspire):
    with open(md_file_path) as md_file:
        xml = md_file.read()
    tree = et.fromstring(xml.encode("utf-8"))
    result = {}
    result["inspire"] =  inspire
    if inspire:
        result["inspire_theme_uri"] = get_inspire_theme_url(tree)
    ogc_service_type = get_ogc_servicetype(tree)
    result["ogc_service_type"] = ogc_service_type
    service_cap_url_key = get_service_cap_key(result["ogc_service_type"])
    result[service_cap_url_key] = get_service_capabilities_url(tree)

    result["md_standardname"] = get_metadatastandardname(tree)
    result["md_standardversion"] =  get_metadatastandardversion(tree)
    result["md_identifier"] = get_mdidentifier(tree)
    result["datestamp"] =  get_datestamp(tree)
    result["service_title"] =  get_title(tree)
    result["service_abstract"] =  get_abstract(tree)
    result["service_publication_date"] = get_md_date(tree, "publication")
    result["service_revision_date"] = get_md_date(tree, "revision")
    result["service_creation_date"] = get_md_date(tree, "creation")
    result["keywords"] = get_keywords(tree)
    result["service_gebruiksbeperkingen"] = get_uselimitations(tree)
    result["service_licentie"] = get_license(tree)
    result["bbox"] = get_bbox(tree)
    result["service_type"] = get_servicetype(tree)
    result["dataset_md_identifier"] = get_dataset_md_identifier(tree)
    result["dataset_source_identifier"] = get_dataset_source_identifier(tree)
    result["service_contact"] = get_contact(tree, f"{XPATH_SERVICE_ID}/gmd:pointOfContact/gmd:CI_ResponsibleParty")
    result["md_contact"] = get_contact(tree, f"{XPATH_METADATA}/gmd:contact/gmd:CI_ResponsibleParty")
    result["thumbnails"] = get_thumbnails(tree)
    print(json.dumps(result))


def get_service_cap_key(ogc_service_type):
    ogc_service_type_lower = ogc_service_type.lower()
    return f"service_capabilities_url_{ogc_service_type_lower}"

def get_ogc_servicetype(etree):
    xpath = f"{XPATH_METADATA}/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource"
    xpath_prot = f"{xpath}/gmd:protocol/gco:CharacterString"
    protocol =  get_single_xpath_value(etree, xpath_prot)
    if protocol == None:
        xpath_prot = f"{xpath}/gmd:protocol/gmx:Anchor"
    protocol =  get_single_xpath_value(etree, xpath_prot)
    if not protocol in SERVICE_TYPES:
        raise ValueError(f"unknown protocol found in gmd:CI_OnlineResource {protocol}")
    return SERVICE_TYPES[protocol]

def get_service_capabilities_url(etree):
    xpath = f"{XPATH_METADATA}/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:linkage/gmd:URL"
    url = get_single_xpath_value(etree, xpath)
    if not is_url(url):
        raise ValueError(f"no valid url found for gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource: {url}")
    return url

def get_contact(etree, base):
    xpath_organisationname = f"{base}/gmd:organisationName/gco:CharacterString"
    xpath_contact =f"{base}/gmd:contactInfo/gmd:CI_Contact"
    xpath_email = f"{xpath_contact}/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString"
    xpath_url = f"{xpath_contact}/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL"
    xpath_role = f"{base}/gmd:role/gmd:CI_RoleCode/@codeListValue"
    result = {}
    result["organisationname"] = get_single_xpath_value(etree, xpath_organisationname)
    result["email"] = get_single_xpath_value(etree, xpath_email)
    result["url"] = get_single_xpath_value(etree, xpath_url)
    result["role"] = get_single_xpath_att(etree, xpath_role)
    return result

def get_mdidentifier(etree):
    xpath = f"{XPATH_METADATA}/gmd:fileIdentifier/gco:CharacterString"
    return get_single_xpath_value(etree, xpath)

def get_datestamp(etree):
    xpath = f"{XPATH_METADATA}/gmd:dateStamp/gco:Date"
    return get_single_xpath_value(etree, xpath)

def get_metadatastandardname(etree):
    xpath = f"{XPATH_METADATA}/gmd:metadataStandardName/gco:CharacterString"
    return get_single_xpath_value(etree, xpath)
    
def get_metadatastandardversion(etree):
    xpath = f"{XPATH_METADATA}/gmd:metadataStandardVersion/gco:CharacterString"
    return get_single_xpath_value(etree, xpath)
    
def get_md_date(etree, date_type):
    xpath = f"{XPATH_SERVICE_ID}/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue='{date_type}']/../../gmd:date/gco:Date"
    return get_single_xpath_value(etree, xpath)
    
def get_abstract(etree):
    xpath = f"{XPATH_SERVICE_ID}/gmd:abstract/gco:CharacterString"
    return get_single_xpath_value(etree, xpath)
                      
def get_title(etree):
    xpath = f"{XPATH_SERVICE_ID}/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString"
    return get_single_xpath_value(etree, xpath)
                   
def get_keywords(etree):
    result = etree.xpath(f'{XPATH_SERVICE_ID}/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString', namespaces=NS)
    keywords = []
    for kw in result:
        keywords.append(kw.text)
    return keywords

def get_inspire_theme_url(etree):
    xpath = f"{XPATH_SERVICE_ID}/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/\
        gmd:title/gmx:Anchor[@xlink:href='http://www.eionet.europa.eu/gemet/inspire_themes']/../../../../gmd:keyword/gmx:Anchor/@xlink:href"
    uri = get_single_xpath_att(etree, xpath)
    if uri:
        uri = uri.replace("http://", "https://")
    return uri

def get_uselimitations(etree):
    xpath = f"{XPATH_SERVICE_ID}/gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString"
    return get_single_xpath_value(etree, xpath)

def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False


def get_license(etree):
    xpath_12 = f"{XPATH_SERVICE_ID}/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString"
    xpath_20 = f"{XPATH_SERVICE_ID}/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gmx:Anchor"
    xpath_20_href = f"{xpath_20}/@xlink:href"

    # first try nl profiel 2.0
    result = {}
    xpath_result = etree.xpath(xpath_20_href, namespaces=NS)
    if xpath_result :
        result["url"] = xpath_result[0]
        result["description"] = get_single_xpath_value(etree, xpath_20)
    else:
        # otherwise try nl profiel 1.2
        xpath_result = etree.xpath(xpath_12, namespaces=NS)
        if len(xpath_result) <= 1:
            raise ValueError("Unable to determine license from metadata, xpath: gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/")
        result["description"] = xpath_result[0].text
        result["url"] = xpath_result[1].text
    # validate license url
    if not is_url(result["url"]):
        url_val = result["url"]
        raise ValueError(f"could not determine license url in gmd:MD_LegalConstraints, found {url_val}")
    return result
    
def get_thumbnails(etree):
    result = []
    xpath =f"{XPATH_SERVICE_ID}/gmd:graphicOverview/gmd:MD_BrowseGraphic"
    xpath_result = etree.xpath(xpath, namespaces=NS)
    for graphic in xpath_result:
        xpath_file = f"gmd:fileName/gco:CharacterString"
        xpath_description = f"gmd:fileDescription/gco:CharacterString"
        xpath_filetype = f"gmd:fileType/gco:CharacterString"
        graphic_result = {}
        graphic_result["file"] = get_single_xpath_value(graphic, xpath_file)
        graphic_result["description"] = get_single_xpath_value(graphic, xpath_description)
        graphic_result["filetype"] = get_single_xpath_value(graphic, xpath_filetype)
        result.append(graphic_result)
    return result

def get_servicetype(etree):
    xpath = f"{XPATH_SERVICE_ID}/srv:serviceType/gco:LocalName"
    return get_single_xpath_value(etree, xpath)

def get_bbox(etree):
    xpath = f"{XPATH_SERVICE_ID}/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox"
    result = {}
    xpath_west = f"{xpath}/gmd:westBoundLongitude/gco:Decimal"
    xpath_east = f"{xpath}/gmd:eastBoundLongitude/gco:Decimal"
    xpath_north = f"{xpath}/gmd:northBoundLatitude/gco:Decimal"
    xpath_south = f"{xpath}/gmd:southBoundLatitude/gco:Decimal"
    result["minx"] = get_single_xpath_value(etree, xpath_west)
    result["maxx"] = get_single_xpath_value(etree, xpath_east)
    result["maxy"] = get_single_xpath_value(etree, xpath_north)
    result["miny"] = get_single_xpath_value(etree, xpath_south)
    return result

def get_single_xpath_value(etree, xpath):
    result = etree.xpath(xpath, namespaces=NS)
    if result:
        return result[0].text

def get_single_xpath_att(etree, xpath):
    result = etree.xpath(xpath, namespaces=NS)
    if result:
        return result[0]


def get_operateson(etree):
    xpath_uuidref = f"{XPATH_SERVICE_ID}/srv:operatesOn/@uuidref"
    xpath_href = f"{XPATH_SERVICE_ID}/srv:operatesOn/@xlink:href"
    result = {}
    result["uuidref"] = get_single_xpath_att(etree, xpath_uuidref)
    result["href"] = get_single_xpath_att(etree, xpath_href)
    return result

def get_dataset_md_identifier(etree):
    operateson = get_operateson(etree)
    parsed = urlparse(operateson["href"])
    return parse_qs(parsed.query)['id'][0]

def get_dataset_source_identifier(etree):
    operateson = get_operateson(etree)
    return operateson["uuidref"]
                   
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("md_file")
    parser.add_argument('--inspire', dest='inspire', action='store_true')
    parser.add_argument('--no-inspire', dest='inspire', action='store_false')
    args = parser.parse_args()
    main(args.md_file, args.inspire)