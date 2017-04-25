from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from mezzanine.pages.page_processors import processor_for

from hs_core.models import BaseResource, ResourceManager, resource_processor,\
                           CoreMetaData, AbstractMetaDataElement

from lxml import etree


class OriginalFileInfo(AbstractMetaDataElement):

    term = 'OriginalFileInfo'

    fileTypeEnum = (
                    (None, 'Unknown'),
                    ("SHP", "ESRI Shapefiles"),
                    ("ZSHP", "Zipped ESRI Shapefiles"),
                    ("KML", "KML"),
                    ("KMZ", "KMZ"),
                    ("GML", "GML"),
                    ("SQLITE", "SQLite")
                   )
    fileType = models.TextField(max_length=128, choices=fileTypeEnum, default=None)
    baseFilename = models.TextField(max_length=256, null=False, blank=False)
    fileCount = models.IntegerField(null=False, blank=False, default=0)
    filenameString = models.TextField(null=True, blank=True)

    class Meta:
        # OriginalFileInfo element is not repeatable
        unique_together = ("content_type", "object_id")


class OriginalCoverage(AbstractMetaDataElement):
    term = 'OriginalCoverage'

    northlimit = models.FloatField(null=False, blank=False)
    southlimit = models.FloatField(null=False, blank=False)
    westlimit = models.FloatField(null=False, blank=False)
    eastlimit = models.FloatField(null=False, blank=False)
    projection_string = models.TextField(null=True, blank=True)
    projection_name = models.TextField(max_length=256, null=True, blank=True)
    datum = models.TextField(max_length=256, null=True, blank=True)
    unit = models.TextField(max_length=256, null=True, blank=True)

    class Meta:
        # OriginalCoverage element is not repeatable
        unique_together = ("content_type", "object_id")


class FieldInformation(AbstractMetaDataElement):
    term = 'FieldInformation'

    fieldName = models.CharField(max_length=128, null=False, blank=False)
    fieldType = models.CharField(max_length=128, null=False, blank=False)
    fieldTypeCode = models.CharField(max_length=50, null=True, blank=True)
    fieldWidth = models.IntegerField(null=True, blank=True)
    fieldPrecision = models.IntegerField(null=True, blank=True)


class GeometryInformation(AbstractMetaDataElement):
    term = 'GeometryInformation'

    featureCount = models.IntegerField(null=False, blank=False, default=0)
    geometryType = models.CharField(max_length=128, null=False, blank=False)

    class Meta:
        # GeometryInformation element is not repeatable
        unique_together = ("content_type", "object_id")


class GeographicFeatureResource(BaseResource):
    objects = ResourceManager("GeographicFeatureResource")

    @property
    def metadata(self):
        md = GeographicFeatureMetaData()
        return self._get_metadata(md)

    @classmethod
    def get_supported_upload_file_types(cls):

        # See Shapefile format:
        # http://resources.arcgis.com/en/help/main/10.2/index.html#//005600000003000000
        return (".zip", ".shp", ".shx", ".dbf", ".prj",
                ".sbx", ".sbn", ".cpg", ".xml", ".fbn",
                ".fbx", ".ain", ".aih", ".atx", ".ixs",
                ".mxs")

    def get_hs_term_dict(self):
        # get existing hs_term_dict from base class
        hs_term_dict = super(GeographicFeatureResource, self).get_hs_term_dict()
        geometryinformation = self.metadata.geometryinformation
        if geometryinformation is not None:
            hs_term_dict["HS_GFR_FEATURE_COUNT"] = geometryinformation.featureCount
        else:
            hs_term_dict["HS_GFR_FEATURE_COUNT"] = 0
        return hs_term_dict

    class Meta:
        verbose_name = 'Geographic Feature (ESRI Shapefiles)'
        proxy = True


processor_for(GeographicFeatureResource)(resource_processor)


class GeographicFeatureMetaDataMixin(models.Model):
    """This class must be the first class in the multi-inheritance list of classes"""
    geometryinformations = GenericRelation(GeometryInformation)
    fieldinformations = GenericRelation(FieldInformation)
    originalcoverages = GenericRelation(OriginalCoverage)
    originalfileinfos = GenericRelation(OriginalFileInfo)

    class Meta:
        abstract = True

    @property
    def geometryinformation(self):
        return self.geometryinformations.all().first()

    @property
    def originalcoverage(self):
        return self.originalcoverages.all().first()

    @property
    def originalfileinfo(self):
        return self.originalfileinfos.all().first()

    @classmethod
    def get_supported_element_names(cls):
        # get the names of all core metadata elements
        elements = super(GeographicFeatureMetaDataMixin, cls).get_supported_element_names()
        # add the name of any additional element to the list
        elements.append('FieldInformation')
        elements.append('OriginalCoverage')
        elements.append('GeometryInformation')
        elements.append('OriginalFileInfo')
        return elements

    def has_all_required_elements(self):
        if self.get_required_missing_elements():
            return False
        return True

    def get_required_missing_elements(self):  # show missing required meta
        missing_required_elements = super(GeographicFeatureMetaDataMixin, self). \
            get_required_missing_elements()
        if not (self.coverages.all().filter(type='box').first() or
                self.coverages.all().filter(type='point').first()):
            missing_required_elements.append('Spatial Coverage')
        if not self.originalcoverage:
            missing_required_elements.append('Spatial Reference')
        if not self.geometryinformation:
            missing_required_elements.append('Geometry Information')
        if not self.originalfileinfo:
            missing_required_elements.append('Resource File Information')

        return missing_required_elements

    def delete_all_elements(self):
        super(GeographicFeatureMetaDataMixin, self).delete_all_elements()
        self.geometryinformations.all().delete()
        self.fieldinformations.all().delete()
        self.originalcoverages.all().delete()
        self.originalfileinfos.all().delete()


class GeographicFeatureMetaData(GeographicFeatureMetaDataMixin, CoreMetaData):

    @property
    def resource(self):
        return GeographicFeatureResource.objects.filter(object_id=self.id).first()

    def get_xml(self, pretty_print=True):
        # get the xml string representation of the core metadata elements
        xml_string = super(GeographicFeatureMetaData, self).get_xml(pretty_print=False)

        # create an etree xml object
        RDF_ROOT = etree.fromstring(xml_string)

        # get root 'Description' element that contains all other elements
        container = RDF_ROOT.find('rdf:Description', namespaces=self.NAMESPACES)

        if self.originalfileinfo:
            originalfileinfo_fields = ['fileType', 'fileCount', 'baseFilename', 'filenameString']
            self.add_metadata_element_to_xml(container,
                                             self.originalfileinfo,
                                             originalfileinfo_fields)

        if self.geometryinformation:
            geometryinformation_fields = ['geometryType', 'featureCount']
            self.add_metadata_element_to_xml(container,
                                             self.geometryinformation,
                                             geometryinformation_fields)

        for field_info in self.fieldinformations.all():
            field_info_fields = ['fieldName', 'fieldType',
                                 'fieldTypeCode', 'fieldWidth', 'fieldPrecision']
            self.add_metadata_element_to_xml(container, field_info, field_info_fields)

        if self.originalcoverage:
            ori_coverage = self.originalcoverage
            cov = etree.SubElement(container, '{%s}spatialReference' % self.NAMESPACES['hsterms'])
            cov_term = '{%s}' + 'box'
            coverage_terms = etree.SubElement(cov, cov_term % self.NAMESPACES['hsterms'])
            rdf_coverage_value = etree.SubElement(coverage_terms,
                                                  '{%s}value' % self.NAMESPACES['rdf'])
            # original coverage is of box type
            cov_value = 'northlimit=%s; eastlimit=%s; southlimit=%s; westlimit=%s; units=%s' \
                        % (ori_coverage.northlimit, ori_coverage.eastlimit,
                           ori_coverage.southlimit, ori_coverage.westlimit, ori_coverage.unit)

            cov_value = cov_value + '; projection_name=%s' % \
                                    ori_coverage.projection_name + '; datum=%s' % \
                                    ori_coverage.datum + '; projection_string=%s' % \
                                    ori_coverage.projection_string

            rdf_coverage_value.text = cov_value

        return etree.tostring(RDF_ROOT, pretty_print=pretty_print)
