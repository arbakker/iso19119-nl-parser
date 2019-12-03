import lxml.etree as et
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from .util import is_url, get_service_cap_key


class ServiceRecord():
    def __init__(self, file_path):
        xpath_metadata = "/gmd:MD_Metadata"
        with open(file_path) as md_file:
            xml = md_file.read()
        self.etree = et.fromstring(xml.encode("utf-8"))
        self.xpath_metadata = xpath_metadata
        self.xpath_service_id = f"{xpath_metadata}/gmd:identificationInfo/srv:SV_ServiceIdentification"
        self.ns = {"gmx": "http://www.isotc211.org/2005/gmx", "gmd": "http://www.isotc211.org/2005/gmd", "csw": "http://www.opengis.net/cat/csw/2.0.2", "gco": "http://www.isotc211.org/2005/gco", "gml": "http://www.opengis.net/gml",
                   "gmx": "http://www.isotc211.org/2005/gmx", "gsr": "http://www.isotc211.org/2005/gsr", "gts": "http://www.isotc211.org/2005/gts", "srv": "http://www.isotc211.org/2005/srv", "xlink": "http://www.w3.org/1999/xlink", "geonet": "http://www.fao.org/geonetwork"}
        self.service_types = {
            "OGC:CSW": "CSW",
            "OGC:WMS": "WMS",
            "OGC:WMTS": "WMTS",
            "OGC:WFS": "WFS",
            "OGC:WCS": "WCS",
            "OGC:SOS": "SOS",
            "INSPIRE Atom": "ATOM",
            "UKST": "TMS"
        }

    def get_single_xpath_value(self, xpath, etree=None):
        if etree is None:
            etree = self.etree
        result = etree.xpath(xpath, namespaces=self.ns)
        if result:
            return result[0].text
        return None

    def get_single_xpath_att(self, xpath):
        result = self.etree.xpath(xpath, namespaces=self.ns)
        if result:
            return result[0]
        return None

    def get_ogc_servicetype(self):
        xpath = f"{self.xpath_metadata}/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource"
        xpath_prot = f"{xpath}/gmd:protocol/gco:CharacterString"
        protocol = self.get_single_xpath_value(xpath_prot)
        if protocol is None:
            xpath_prot = f"{xpath}/gmd:protocol/gmx:Anchor"
        protocol = self.get_single_xpath_value(xpath_prot)
        if not protocol in self.service_types:
            raise ValueError(
                f"unknown protocol found in gmd:CI_OnlineResource {protocol}")
        return self.service_types[protocol]

    def get_service_capabilities_url(self):
        xpath = f"{self.xpath_metadata}/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:linkage/gmd:URL"
        url = self.get_single_xpath_value(xpath)
        if not is_url(url):
            raise ValueError(
                f"no valid url found for gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource: {url}")
        return url

    def get_contact(self, base):
        xpath_organisationname = f"{base}/gmd:organisationName/gco:CharacterString"
        xpath_contact = f"{base}/gmd:contactInfo/gmd:CI_Contact"
        xpath_email = f"{xpath_contact}/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString"
        xpath_url = f"{xpath_contact}/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL"
        xpath_role = f"{base}/gmd:role/gmd:CI_RoleCode/@codeListValue"
        result = {}
        result["organisationname"] = self.get_single_xpath_value(
            xpath_organisationname)
        result["email"] = self.get_single_xpath_value(xpath_email)
        result["url"] = self.get_single_xpath_value(xpath_url)
        result["role"] = self.get_single_xpath_att(xpath_role)
        return result

    def get_mdidentifier(self):
        xpath = f"{self.xpath_metadata}/gmd:fileIdentifier/gco:CharacterString"
        return self.get_single_xpath_value(xpath)

    def get_datestamp(self):
        xpath = f"{self.xpath_metadata}/gmd:dateStamp/gco:Date"
        return self.get_single_xpath_value(xpath)

    def get_metadatastandardname(self):
        xpath = f"{self.xpath_metadata}/gmd:metadataStandardName/gco:CharacterString"
        return self.get_single_xpath_value(xpath)

    def get_metadatastandardversion(self):
        xpath = f"{self.xpath_metadata}/gmd:metadataStandardVersion/gco:CharacterString"
        return self.get_single_xpath_value(xpath)

    def get_md_date(self, date_type):
        xpath = f"{self.xpath_service_id}/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue='{date_type}']/../../gmd:date/gco:Date"
        return self.get_single_xpath_value(xpath)

    def get_abstract(self):
        xpath = f"{self.xpath_service_id}/gmd:abstract/gco:CharacterString"
        return self.get_single_xpath_value(xpath)

    def get_title(self):
        xpath = f"{self.xpath_service_id}/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString"
        return self.get_single_xpath_value(xpath)

    def get_keywords(self):
        result = self.etree.xpath(
            f'{self.xpath_service_id}/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString', namespaces=self.ns)
        keywords = []
        for kw in result:
            keywords.append(kw.text)
        return keywords

    def get_inspire_theme_url(self):
        xpath = f"{self.xpath_service_id}/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/\
            gmd:title/gmx:Anchor[@xlink:href='http://www.eionet.europa.eu/gemet/inspire_themes']/../../../../gmd:keyword/gmx:Anchor/@xlink:href"
        uri = self.get_single_xpath_att(xpath)
        if uri:
            uri = uri.replace("http://", "https://")
        return uri

    def get_uselimitations(self):
        xpath = f"{self.xpath_service_id}/gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString"
        return self.get_single_xpath_value(xpath)

    def get_license(self):
        xpath_12 = f"{self.xpath_service_id}/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString"
        xpath_20 = f"{self.xpath_service_id}/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gmx:Anchor"
        xpath_20_href = f"{xpath_20}/@xlink:href"

        # first try nl profiel 2.0
        result = {}
        xpath_result = self.etree.xpath(xpath_20_href, namespaces=self.ns)
        if xpath_result:
            result["url"] = xpath_result[0]
            result["description"] = self.get_single_xpath_value(xpath_20)
        else:
            # otherwise try nl profiel 1.2
            xpath_result = self.etree.xpath(xpath_12, namespaces=self.ns)
            if len(xpath_result) <= 1:
                raise ValueError(
                    "Unable to determine license from metadata, xpath: gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/")
            result["description"] = xpath_result[0].text
            result["url"] = xpath_result[1].text
        # validate license url
        if not is_url(result["url"]):
            url_val = result["url"]
            raise ValueError(
                f"could not determine license url in gmd:MD_LegalConstraints, found {url_val}")
        return result

    def get_thumbnails(self):
        result = []
        xpath = f"{self.xpath_service_id}/gmd:graphicOverview/gmd:MD_BrowseGraphic"
        xpath_result = self.etree.xpath(xpath, namespaces=self.ns)
        for graphic in xpath_result:
            xpath_file = f"gmd:fileName/gco:CharacterString"
            xpath_description = f"gmd:fileDescription/gco:CharacterString"
            xpath_filetype = f"gmd:fileType/gco:CharacterString"
            graphic_result = {}
            graphic_result["file"] = self.get_single_xpath_value(
                xpath_file, graphic)
            graphic_result["description"] = self.get_single_xpath_value(
                xpath_description, graphic)
            graphic_result["filetype"] = self.get_single_xpath_value(
                xpath_filetype, graphic)
            result.append(graphic_result)
        return result

    def get_servicetype(self):
        xpath = f"{self.xpath_service_id}/srv:serviceType/gco:LocalName"
        return self.get_single_xpath_value(xpath)

    def get_bbox(self):
        xpath = f"{self.xpath_service_id}/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox"
        result = {}
        xpath_west = f"{xpath}/gmd:westBoundLongitude/gco:Decimal"
        xpath_east = f"{xpath}/gmd:eastBoundLongitude/gco:Decimal"
        xpath_north = f"{xpath}/gmd:northBoundLatitude/gco:Decimal"
        xpath_south = f"{xpath}/gmd:southBoundLatitude/gco:Decimal"
        result["minx"] = self.get_single_xpath_value(xpath_west)
        result["maxx"] = self.get_single_xpath_value(xpath_east)
        result["maxy"] = self.get_single_xpath_value(xpath_north)
        result["miny"] = self.get_single_xpath_value(xpath_south)
        return result

    def get_operateson(self):
        xpath_uuidref = f"{self.xpath_service_id}/srv:operatesOn/@uuidref"
        xpath_href = f"{self.xpath_service_id}/srv:operatesOn/@xlink:href"
        result = {}
        result["uuidref"] = self.get_single_xpath_att(xpath_uuidref)
        result["href"] = self.get_single_xpath_att(xpath_href)
        return result

    def get_dataset_md_identifier(self):
        operateson = self.get_operateson()
        parsed = urlparse(operateson["href"])
        return parse_qs(parsed.query)['id'][0]

    def get_dataset_source_identifier(self):
        operateson = self.get_operateson()
        return operateson["uuidref"]

    def convert_to_dictionary(self, inspire):
        result = {}
        result["inspire"] = inspire
        if inspire:
            result["inspire_theme_uri"] = self.get_inspire_theme_url()
        ogc_service_type = self.get_ogc_servicetype()
        result["ogc_service_type"] = ogc_service_type
        service_cap_url_key = get_service_cap_key(result["ogc_service_type"])
        result[service_cap_url_key] = self.get_service_capabilities_url()
        result["md_standardname"] = self.get_metadatastandardname()
        result["md_standardversion"] = self.get_metadatastandardversion()
        result["md_identifier"] = self.get_mdidentifier()
        result["datestamp"] = self.get_datestamp()
        result["service_title"] = self.get_title()
        result["service_abstract"] = self.get_abstract()
        result["service_publication_date"] = self.get_md_date("publication")
        result["service_revision_date"] = self.get_md_date("revision")
        result["service_creation_date"] = self.get_md_date("creation")
        result["keywords"] = self.get_keywords()
        result["service_gebruiksbeperkingen"] = self.get_uselimitations()
        result["service_licentie"] = self.get_license()
        result["bbox"] = self.get_bbox()
        result["service_type"] = self.get_servicetype()
        result["dataset_md_identifier"] = self.get_dataset_md_identifier()
        result["dataset_source_identifier"] = self.get_dataset_source_identifier()
        result["service_contact"] = self.get_contact(
             f"{self.xpath_service_id}/gmd:pointOfContact/gmd:CI_ResponsibleParty")
        result["md_contact"] = self.get_contact(
             f"{self.xpath_metadata}/gmd:contact/gmd:CI_ResponsibleParty")
        result["thumbnails"] = self.get_thumbnails()
        return result
