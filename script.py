#!/usr/bin/env python3
import argparse
import json
import lxml.etree as et

NS = {"gmd": "http://www.isotc211.org/2005/gmd","csw": "http://www.opengis.net/cat/csw/2.0.2","gco": "http://www.isotc211.org/2005/gco","gml": "http://www.opengis.net/gml","gmx": "http://www.isotc211.org/2005/gmx","gsr": "http://www.isotc211.org/2005/gsr","gts": "http://www.isotc211.org/2005/gts","srv": "http://www.isotc211.org/2005/srv","xlink":"http://www.w3.org/1999/xlink", "geonet":"http://www.fao.org/geonetwork" }

XPATH_METADATA="/gmd:MD_Metadata"
XPATH_SERVICE_ID=f"{XPATH_METADATA}/gmd:identificationInfo/srv:SV_ServiceIdentification"

def main(md_file_path):
    with open(md_file_path) as md_file:
        xml = md_file.read()
    tree = et.fromstring(xml.encode("utf-8"))
    result = {}
    result["md_standardname"] = get_metadatastandardname(tree)
    result["md_standardversion"] =  get_metadatastandardversion(tree)
    result["md_identifier"] = get_mdidentifier(tree)
    result["datestamp"] =  get_datestamp(tree)
    result["title"] =  get_title(tree)
    result["abstract"] =  get_abstract(tree)
    result["publication_date"] = get_md_date(tree, "publication")
    result["revision_date"] = get_md_date(tree, "revision")
    result["creation_date"] = get_md_date(tree, "creation")
    result["keywords"] = get_keywords(tree)
    result["uselimitations"] = get_uselimitations(tree)
    result["securityconstraints"] = get_securityconstraints(tree)
    result["bbox"] = get_bbox(tree)
    result["temporal_extent"] = get_temporal_extent(tree)
    result["service_type"] = get_servicetype(tree)
    result["distribution"] = get_distribution(tree)
    result["operates_on"] = get_operateson(tree)
    result["service_contact"] = get_contact(tree, f"{XPATH_SERVICE_ID}/gmd:pointOfContact/gmd:CI_ResponsibleParty")
    result["md_contact"] = get_contact(tree, f"{XPATH_METADATA}/gmd:contact/gmd:CI_ResponsibleParty")
    print(json.dumps(result))

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
    result = etree.xpath(f'{XPATH_METADATA}/gmd:fileIdentifier/gco:CharacterString', namespaces=NS)
    if result:
        return result[0].text

def get_datestamp(etree):
    result = etree.xpath(f'{XPATH_METADATA}/gmd:dateStamp/gco:Date', namespaces=NS)
    if result:
        return result[0].text

def get_metadatastandardname(etree):
    xpath = f"{XPATH_METADATA}/gmd:metadataStandardName/gco:CharacterString"
    return get_single_xpath_value(etree, xpath)

def get_metadatastandardversion(etree):
    xpath = f"{XPATH_METADATA}/gmd:metadataStandardVersion/gco:CharacterString"
    return get_single_xpath_value(etree, xpath)


def get_md_date(etree, date_type):
    result = etree.xpath(f"{XPATH_SERVICE_ID}/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue='{date_type}']/../../gmd:date/gco:Date", namespaces=NS)
    if result:
        return result[0].text

def get_abstract(etree):
    result = etree.xpath(f'{XPATH_SERVICE_ID}/gmd:abstract/gco:CharacterString', namespaces=NS)
    if result:
        return result[0].text
                  
def get_title(etree):
    result = etree.xpath(f'{XPATH_SERVICE_ID}/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces=NS)
    if result:
        return result[0].text
               
def get_keywords(etree):
    result = etree.xpath(f'{XPATH_SERVICE_ID}/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString', namespaces=NS)
    keywords = []
    for kw in result:
        keywords.append(kw.text)
    return keywords

def get_uselimitations(etree):
    result = etree.xpath(f'{XPATH_SERVICE_ID}/gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString', namespaces=NS)
    if result:
        return result[0].text

def get_securityconstraints(etree):
    result = etree.xpath(f'{XPATH_SERVICE_ID}/gmd:resourceConstraints/gmd:MD_SecurityConstraints/gmd:classification/gmd:MD_ClassificationCode/@codeListValue', namespaces=NS)
    if result:
        return result[0]

def get_temporal_extent(etree):
    xpath = f"{XPATH_SERVICE_ID}/srv:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod"
    xpath_begin = f"{xpath}/gml:begin/gml:TimeInstant/gml:timePosition"
    xpath_end = f"{xpath}/gml:end/gml:TimeInstant/gml:timePosition"
    result = {}
    result["begin"] = get_single_xpath_value(etree, xpath_begin)
    result["end"] = get_single_xpath_value(etree, xpath_end)
    return result

def get_distribution(etree):
    xpath = f"{XPATH_METADATA}/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource"
    xpath_url = f"{xpath}/gmd:linkage/gmd:URL"
    xpath_prot = f"{xpath}/gmd:protocol/gco:CharacterString"
    result = {}
    result["url"] = get_single_xpath_value(etree, xpath_url)
    result["protocol"] = get_single_xpath_value(etree, xpath_prot)
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
    result["west"] = get_single_xpath_value(etree, xpath_west)
    result["east"] = get_single_xpath_value(etree, xpath_east)
    result["north"] = get_single_xpath_value(etree, xpath_south)
    result["south"] = get_single_xpath_value(etree, xpath_north)
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
                   
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("md_file")
    args = parser.parse_args()
    main(args.md_file)