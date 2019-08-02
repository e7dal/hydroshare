import os

from django.core.exceptions import ObjectDoesNotExist

from mezzanine.pages.page_processors import processor_for

from hs_core.models import BaseResource, ResourceManager, ResourceFile, resource_processor


from hs_file_types.models import GenericLogicalFile, FileSetLogicalFile
from hs_file_types.utils import update_target_temporal_coverage, update_target_spatial_coverage


class CompositeResource(BaseResource):
    objects = ResourceManager("CompositeResource")

    discovery_content_type = 'Composite'  # used during discovery

    class Meta:
        verbose_name = 'Composite Resource'
        proxy = True

    @property
    def can_be_public_or_discoverable(self):
        # resource level metadata check
        if not super(CompositeResource, self).can_be_public_or_discoverable:
            return False

        # filetype level metadata check
        for lf in self.logical_files:
            if not lf.metadata.has_all_required_elements():
                return False

        return True

    @property
    def logical_files(self):
        """Returns a list of all logical file type objects associated with this resource """

        lf_list = []
        lf_list.extend(self.filesetlogicalfile_set.all())
        lf_list.extend(self.genericlogicalfile_set.all())
        lf_list.extend(self.geofeaturelogicalfile_set.all())
        lf_list.extend(self.netcdflogicalfile_set.all())
        lf_list.extend(self.georasterlogicalfile_set.all())
        lf_list.extend(self.reftimeserieslogicalfile_set.all())
        lf_list.extend(self.timeserieslogicalfile_set.all())

        return lf_list

    @property
    def can_be_published(self):
        # resource level metadata check
        if not super(CompositeResource, self).can_be_published:
            return False

        # filetype level metadata check
        for lf in self.logical_files:
            if not lf.metadata.has_all_required_elements():
                return False
            # url file cannot be published
            if 'url' in lf.extra_data:
                return False
        return True

    def set_default_logical_file(self):
        """sets an instance of GenericLogicalFile to any resource file objects of this instance
        of the resource that is not already associated with a logical file. """

        for res_file in self.files.all():
            if not res_file.has_logical_file:
                logical_file = GenericLogicalFile.create()
                res_file.logical_file_content_object = logical_file
                res_file.save()

    def get_folder_aggregation_object(self, dir_path):
        """Returns an aggregation (file type) object if the specified folder *dir_path* represents a
         file type aggregation (logical file), otherwise None.

         :param dir_path: Resource file directory path (full folder path starting with resource id)
         for which the aggregation object to be retrieved
        """

        aggregation_path = dir_path[len(self.file_path) + 1:]
        try:
            return self.get_aggregation_by_name(aggregation_path)
        except ObjectDoesNotExist:
            return None

    def get_file_aggregation_object(self, file_path):
        """Returns an aggregation (file type) object if the specified file *file_path* represents a
         file type aggregation (logical file), otherwise None.

         :param file_path: Resource file path (full file path starting with resource id)
         for which the aggregation object to be retrieved
        """
        for res_file in self.files.all():
            if res_file.full_path == file_path:
                if res_file.has_logical_file:
                    return res_file.logical_file
        return None

    def can_set_folder_to_fileset(self, dir_path):
        """Checks if the specified folder *dir_path* can be set to Fileset aggregation

        :param dir_path: Resource file directory path (full folder path starting with resource id)
        for which the FileSet aggregation to be set

        :return If the specified folder is already represents an aggregation or does
        not contain any files then returns False, otherwise True
        """

        if self.get_folder_aggregation_object(dir_path) is not None:
            # target folder is already an aggregation
            return False

        istorage = self.get_irods_storage()
        irods_path = dir_path
        if self.is_federated:
            irods_path = os.path.join(self.resource_federation_path, irods_path)
        store = istorage.listdir(irods_path)
        files_in_folder = ResourceFile.list_folder(self, folder=irods_path, sub_folders=False)

        if not files_in_folder:
            # folder is empty
            # check sub folders for files - if file exist we can set FileSet aggregation
            files_in_sub_folders = ResourceFile.list_folder(self, folder=irods_path,
                                                            sub_folders=True)
            if files_in_sub_folders:
                return True

            return False
        if store[0]:
            # there are folders under dir_path as well as files - FileSet can bet set
            return True

        if len(files_in_folder) > 0:
            return True
        else:
            return False

    @property
    def supports_folders(self):
        """ allow folders for CompositeResources """
        return True

    @property
    def supports_logical_file(self):
        """ if this resource allows associating resource file objects with logical file"""
        return True

    def get_metadata_xml(self, pretty_print=True, include_format_elements=True):
        from lxml import etree

        # get resource level core metadata as xml string
        # for composite resource we don't want the format elements at the resource level
        # as they are included at the aggregation map xml document
        xml_string = super(CompositeResource, self).get_metadata_xml(pretty_print=False,
                                                                     include_format_elements=False)

        # create an etree xml object
        RDF_ROOT = etree.fromstring(xml_string)

        return etree.tostring(RDF_ROOT, pretty_print=pretty_print)

    def create_aggregation_xml_documents(self, aggregation_name=None):
        """Creates aggregation map and metadata xml files for each of the contained aggregations

        :param  aggregation_name: (optional) name of the the specific aggregation for which xml
        documents need to be created
        """

        if aggregation_name is None:
            for aggregation in self.logical_files:
                if aggregation.metadata.is_dirty:
                    aggregation.create_aggregation_xml_documents()
        else:
            try:
                aggregation = self.get_aggregation_by_name(aggregation_name)
                if aggregation.metadata.is_dirty:
                    aggregation.create_aggregation_xml_documents()
            except ObjectDoesNotExist:
                # aggregation_name must be a folder path that doesn't represent an aggregation
                # there may be other aggregations in that folder for which xml documents
                # need to be re-created
                self._recreate_xml_docs_for_folder(new_folder=aggregation_name,
                                                   check_metadata_dirty=True)

    def _recreate_xml_docs_for_folder(self, new_folder, old_folder=None,
                                      check_metadata_dirty=False):
        """Re-creates xml metadata and map documents associated with the specified folder.
        If the *new_folder* represents an aggregation then map and metadata xml documents are
        recreated only for that aggregation. Otherwise, xml documents are created for any
        aggregation that may exist in the specified folder and its sub-folders.

        :param  new_folder: folder for which xml documents need to be re-created
        :param  old_folder: (optional) folder name prior to folder name change to as
        per 'new_folder'
        :param  check_metadata_dirty: if true, then xml files will be created only if the
        aggregation metadata is dirty
        """

        # first check if the the folder represents an aggregation (fileset)
        try:
            aggregation = self.get_aggregation_by_name(new_folder)
            if check_metadata_dirty:
                if aggregation.metadata.is_dirty:
                    aggregation.create_aggregation_xml_documents()
            else:
                aggregation.create_aggregation_xml_documents()
            # for fileset aggregation needs to generate xml files for all containing filesets
            if aggregation.is_fileset:
                for child_aggr in aggregation.get_children():
                    if child_aggr.is_fileset:
                        child_aggr.create_aggregation_xml_documents()

        except ObjectDoesNotExist:
            # create xml map and metadata xml documents for all aggregations that exist
            # in *new_folder* and its sub-folders
            if not new_folder.startswith(self.file_path):
                new_folder = os.path.join(self.file_path, new_folder)

            res_file_objects = ResourceFile.list_folder(self, new_folder)
            aggregations = []
            for res_file in res_file_objects:
                if res_file.has_logical_file and res_file.logical_file not in aggregations:
                    aggregation = res_file.logical_file
                    if not aggregation.is_fileset:
                        aggregations.append(aggregation)

            if old_folder is not None:
                # find all fileset aggregations under the folder *old_folder*
                for fs in FileSetLogicalFile.objects.filter(folder__startswith=old_folder):
                    aggregations.append(fs)

            if check_metadata_dirty:
                aggregations = [aggr for aggr in aggregations if aggr.metadata.is_dirty]

            if new_folder.startswith(self.file_path):
                new_folder = new_folder[len(self.file_path) + 1:]

            for aggregation in aggregations:
                # if we are finding a fileset aggregation here means old_folder is not None
                if aggregation.is_fileset and not aggregation.has_parent:
                    # need to update the folder attribute of the top level fileset aggregations
                    # children filesets of these top level filesets will be updated by the
                    # corresponding top level (parent) fileset
                    aggregation.update_folder(new_folder=new_folder, old_folder=old_folder)
                aggregation.create_aggregation_xml_documents()

    def get_aggregation_by_aggregation_name(self, aggregation_name):
        """Get an aggregation that matches the aggregation dataset_name specified by *dataset_name*
        :param  aggregation_name: aggregation_name (aggregation path) of the aggregation to find
        :return an aggregation object if found
        :raises ObjectDoesNotExist if no matching aggregation is found
        """
        for aggregation in self.logical_files:
            if aggregation.aggregation_name == aggregation_name:
                return aggregation

        raise ObjectDoesNotExist("No matching aggregation was found for "
                                 "name:{}".format(aggregation_name))

    def get_aggregation_by_name(self, name):
        """Get an aggregation that matches the aggregation name specified by *name*
        :param  name: name (aggregation path) of the aggregation to find
        :return an aggregation object if found
        :raises ObjectDoesNotExist if no matching aggregation is found
        """
        for aggregation in self.logical_files:
            # remove the last slash in aggregation_name if any
            if aggregation.aggregation_name.rstrip('/') == name:
                return aggregation

        raise ObjectDoesNotExist("No matching aggregation was found for name:{}".format(name))

    def get_fileset_aggregation_in_path(self, path):
        """Get the first fileset aggregation in the path moving up (towards the root)in the path
        :param  path: directory path in which to search for a fileset aggregation
        :return a fileset aggregation object if found, otherwise None
        """

        def get_fileset(path):
            try:
                aggregation = self.get_aggregation_by_name(path)
                if aggregation.is_fileset:
                    return aggregation
            except ObjectDoesNotExist:
                return None

        while '/' in path:
            fileset = get_fileset(path)
            if fileset is not None:
                return fileset
            path = os.path.dirname(path)
        else:
            return get_fileset(path)

    def recreate_aggregation_xml_docs(self, orig_aggr_name, new_aggr_name):
        """
        When a folder or file representing an aggregation is renamed or moved,
        the associated map and metadata xml documents are deleted
        and then regenerated
        :param  orig_aggr_name: original aggregation name - used for deleting existing
        xml documents
        :param  new_aggr_name: new aggregation name - used for finding a matching
        aggregation so that new xml documents can be recreated
        """

        def delete_old_xml_files(folder=''):
            istorage = self.get_irods_storage()
            # remove file extension from aggregation name (note: aggregation name is a file path
            # for all aggregation types except fileset
            xml_file_name, _ = os.path.splitext(orig_aggr_name)
            meta_xml_file_name = xml_file_name + "_meta.xml"
            map_xml_file_name = xml_file_name + "_resmap.xml"
            if not folder:
                # case of file rename/move for single file aggregation
                meta_xml_file_full_path = os.path.join(self.file_path, meta_xml_file_name)
                map_xml_file_full_path = os.path.join(self.file_path, map_xml_file_name)
            else:
                # case of folder rename - fileset aggregation
                _, meta_xml_file_name = os.path.split(meta_xml_file_name)
                _, map_xml_file_name = os.path.split(map_xml_file_name)
                meta_xml_file_full_path = os.path.join(self.file_path, folder, meta_xml_file_name)
                map_xml_file_full_path = os.path.join(self.file_path, folder, map_xml_file_name)

            if istorage.exists(meta_xml_file_full_path):
                istorage.delete(meta_xml_file_full_path)

            if istorage.exists(map_xml_file_full_path):
                istorage.delete(map_xml_file_full_path)

        # first check if the new_aggr_name is a folder path or file path
        name, ext = os.path.splitext(new_aggr_name)
        is_new_aggr_a_folder = ext == ''

        if is_new_aggr_a_folder:
            delete_old_xml_files(folder=new_aggr_name)
            try:
                # in case of fileset aggregation need to update aggregation folder attribute to the
                # new folder name
                aggregation = self.get_aggregation_by_name(orig_aggr_name)
                if aggregation.is_fileset:
                    # update folder attribute of this fileset aggregation and all nested
                    # fileset aggregations of this aggregation
                    aggregation.update_folder(new_folder=new_aggr_name, old_folder=orig_aggr_name)
            except ObjectDoesNotExist:
                # not renaming a fileset aggregation folder
                pass
            self._recreate_xml_docs_for_folder(new_folder=new_aggr_name, old_folder=orig_aggr_name)
        else:
            # check if there is a matching single file aggregation
            try:
                aggregation = self.get_aggregation_by_name(new_aggr_name)
                delete_old_xml_files()
                aggregation.create_aggregation_xml_documents()
            except ObjectDoesNotExist:
                # the file path *new_aggr_name* is not a single file aggregation - no more
                # action is needed
                pass

    def is_aggregation_xml_file(self, file_path):
        """ determine whether a given file in the file hierarchy is metadata.

        This is true if it is listed as metadata in any logical file.
        """
        if not (file_path.endswith('_meta.xml') or file_path.endswith('_resmap.xml')):
            return False
        for logical_file in self.logical_files:
            if logical_file.metadata_file_path == file_path or \
                    logical_file.map_file_path == file_path:
                return True
        return False

    def supports_rename_path(self, src_full_path, tgt_full_path):
        """checks if file/folder rename/move is allowed
        :param  src_full_path: name of the file/folder path to be renamed
        :param  tgt_full_path: new name for file/folder path
        :return True or False
        """

        if __debug__:
            assert(src_full_path.startswith(self.file_path))
            assert(tgt_full_path.startswith(self.file_path))

        istorage = self.get_irods_storage()

        # need to find out which of the following actions the user is trying to do:
        # renaming a file
        # renaming a folder
        # moving a file
        # moving a folder
        is_renaming_file = False
        is_moving_file = False
        is_moving_folder = False

        tgt_folder, tgt_file_name = os.path.split(tgt_full_path)
        _, tgt_ext = os.path.splitext(tgt_file_name)
        if tgt_ext:
            tgt_file_dir = os.path.dirname(tgt_full_path)
        else:
            tgt_file_dir = tgt_full_path

        src_folder, src_file_name = os.path.split(src_full_path)
        _, src_ext = os.path.splitext(src_file_name)
        if src_ext:
            src_file_dir = os.path.dirname(src_full_path)
        else:
            src_file_dir = src_full_path

        if src_ext and tgt_ext:
            is_renaming_file = True
        elif src_ext:
            is_moving_file = True
        elif not istorage.exists(tgt_file_dir):
            # renaming folder - no restriction
            return True
        else:
            is_moving_folder = True

        def check_file_rename_or_move():
            # see if the folder containing the file represents an aggregation
            if src_file_dir != self.file_path:
                aggregation_path = src_file_dir[len(self.file_path) + 1:]
                try:
                    aggregation = self.get_aggregation_by_name(aggregation_path)
                    return aggregation.supports_resource_file_rename
                except ObjectDoesNotExist:
                    # check if the source file represents an aggregation
                    # get source resource file object from source file path
                    src_res_file = ResourceFile.get(self, src_file_name, aggregation_path)
                    aggregation = src_res_file.logical_file
                    if aggregation is None:
                        raise ObjectDoesNotExist
                    if is_renaming_file:
                        return aggregation.supports_resource_file_rename
                    else:
                        return aggregation.supports_resource_file_move
            else:
                # get source resource file object from source file path
                src_res_file = ResourceFile.get(self, src_file_name)
                # check if the source file is part of an aggregation
                aggregation = src_res_file.logical_file
                if aggregation is None:
                    raise ObjectDoesNotExist("No aggregation found at {}".format(src_file_name))

                if is_renaming_file:
                    return aggregation.supports_resource_file_rename
                else:
                    return aggregation.supports_resource_file_move

        if is_renaming_file:
            # see if the folder containing the file represents an aggregation
            try:
                can_rename = check_file_rename_or_move()
                return can_rename
            except ObjectDoesNotExist:
                return True

        elif is_moving_file:
            # check source - see if the folder containing the file represents an aggregation
            try:
                can_move = check_file_rename_or_move()
                return can_move
            except ObjectDoesNotExist:
                return True

        elif is_moving_folder:
            return True

    def can_add_files(self, target_full_path):
        """
        checks if file(s) can be uploaded to the specified *target_full_path*
        :param target_full_path: full folder path name where file needs to be uploaded to
        :return: True or False
        """
        istorage = self.get_irods_storage()
        if istorage.exists(target_full_path):
            path_to_check = target_full_path
        else:
            return False

        if not path_to_check.endswith("data/contents"):
            # it is not the base directory - it must be a directory under base dir
            if path_to_check.startswith(self.file_path):
                aggregation_path = path_to_check[len(self.file_path) + 1:]
            else:
                aggregation_path = path_to_check
            try:
                aggregation = self.get_aggregation_by_name(aggregation_path)
                return aggregation.supports_resource_file_add
            except ObjectDoesNotExist:
                # target path doesn't represent an aggregation - so it is OK to add a file
                pass
        return True

    def supports_zip(self, folder_to_zip):
        """check if the given folder can be zipped or not"""

        # find all the resource files in the folder to be zipped
        # this is being passed both qualified and unqualified paths!

        full_path = folder_to_zip
        if not full_path.startswith(self.file_path):
            full_path = os.path.join(self.file_path, full_path)
        # get all resource files at full_path and its sub-folders
        res_file_objects = ResourceFile.list_folder(self, full_path)

        # check any logical file associated with the resource file supports zip functionality
        for res_file in res_file_objects:
            if res_file.has_logical_file:
                if not res_file.logical_file.supports_zip:
                    return False
        return True

    def supports_delete_folder_on_zip(self, original_folder):
        """check if the specified folder can be deleted at the end of zipping that folder"""

        # find all the resource files in the folder to be deleted
        # this is being passed both qualified and unqualified paths!
        full_path = original_folder
        if not full_path.startswith(self.file_path):
            full_path = os.path.join(self.file_path, full_path)

        # get all resource files at full_path and its sub-folders
        res_file_objects = ResourceFile.list_folder(self, full_path)

        # check any logical file associated with the resource file supports deleting the folder
        # after its zipped
        for res_file in res_file_objects:
            if res_file.has_logical_file:
                if not res_file.logical_file.supports_delete_folder_on_zip:
                    return False
        return True

    def get_missing_file_type_metadata_info(self):
        # this is used in page pre-processor to build the context
        # so that the landing page can show what metadata items are missing for each
        # logical file/aggregation
        metadata_missing_info = []
        for lfo in self.logical_files:
            if not lfo.metadata.has_all_required_elements():
                missing_elements = lfo.metadata.get_required_missing_elements()
                metadata_missing_info.append({'file_path': lfo.aggregation_name,
                                              'missing_elements': missing_elements})
        return metadata_missing_info

    def delete_coverage(self, coverage_type):
        """Deletes coverage data for the resource
        :param coverage_type: A value of either 'spatial' or 'temporal
        :return:
        """
        if coverage_type.lower() == 'spatial' and self.metadata.spatial_coverage:
            self.metadata.spatial_coverage.delete()
            self.metadata.is_dirty = True
            self.metadata.save()
        elif coverage_type.lower() == 'temporal' and self.metadata.temporal_coverage:
            self.metadata.temporal_coverage.delete()
            self.metadata.is_dirty = True
            self.metadata.save()

    def update_coverage(self):
        """Update resource spatial and temporal coverage based on the corresponding coverages
        from all the contained aggregations (logical file) only if the resource coverage is not
        already set"""

        # update resource spatial coverage only if there is no spatial coverage already
        if self.metadata.spatial_coverage is None:
            self.update_spatial_coverage()

        # update resource temporal coverage only if there is no temporal coverage already
        if self.metadata.temporal_coverage is None:
            self.update_temporal_coverage()

    def update_spatial_coverage(self):
        """Updates resource spatial coverage based on the contained spatial coverages of
        aggregations (file type). Note: This action will overwrite any existing resource spatial
        coverage data.
        """

        update_target_spatial_coverage(self)

    def update_temporal_coverage(self):
        """Updates resource temporal coverage based on the contained temporal coverages of
        aggregations (file type). Note: This action will overwrite any existing resource temporal
        coverage data.
        """

        update_target_temporal_coverage(self)


# this would allow us to pick up additional form elements for the template before the template
# is displayed
processor_for(CompositeResource)(resource_processor)
