import os


class Utils:

    """
    Class to store util functions
    """

    def __init__(self):
        """
        Defines the allowed archive extensions and their extraction methods
        """

        self.allowed_archive_exts = [".tar.gz", ".tgz"]
        self.file_extract_methods = {".tar.gz": "tar xvf ",
                ".tgz": "tar xvf "}

    def get_basename(self, url_or_filepath):
        """
        Returns the basename of a url or path
        """

        from posixpath import basename
        return basename(url_or_filepath)

    def get_basename_prefix(self, url_or_filepath):
        filename = self.get_basename(url_or_filepath)
        for ext in self.allowed_archive_exts:
            if filename.endswith(ext):
                return filename.replace(ext, "")
        return filename

    def parse_boolean(self, boolval):
        """
        Parses a boolean string from the config file into a Boolean type
        """

        bool_map = {"true": True, "false": False}
        if boolval == True or boolval == False:
            return boolval
        return bool_map[boolval.strip().lower()]

    def get_fab_path(self):
        """
        Returns the parent path of the currently running fabric file
        """

        return os.path.abspath(os.path.join(env.real_fabfile, ".."))



class Templates:


    def template(self, template_file, template_map):
        ftmpl = open(template_file)
        fcontents = ftmpl.read()
        return fcontents % template_map
  

    def name_from_template(self, file_name):
        from posixpath import basename
        print "generating from template file ", file_name
        return basename(file_name)[0:-5]

    
    def new_file(
        self,
        template_file,
        template_map,
        output_dir,
        ):
        contents = self.template(template_file, template_map)
        new_file = self.name_from_template(template_file)
        print "new file from template going to be created ", new_file
        fnewfile = open("%(out_dir)s/%(file.conf)s" % {"out_dir"
                        : output_dir, "file.conf": new_file}, "w")
        fnewfile.write(contents)
        fnewfile.close()
        print new_file, " was created in ", output_dir



