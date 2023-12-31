import yaml
import os
import shutil
import fnmatch
import subprocess

class Environment:

    CONFIG_FILENAME = "config.yaml"
    START_FILENAME_PATTERN = "xxx!Start.ico"

    def __init__(self):
        with open(self.CONFIG_FILENAME, "r") as f:
            self.config_data = yaml.safe_load(f)

    def get_cdrom_path(self):
        return self.config_data["PATH"]["CDROM"]
    
    def get_cbm_archive_path(self):
        return self.config_data["PATH"]["ARCHIVE"]
    
    def get_cbm_import_path(self):
        return self.config_data["PATH"]["IMPORT"]
    
    def get_twic_baseurl(self):
        return self.config_data["URL"]["TWIC_BASE"]
    
    def get_next_cbm_nr(self):
        return int(self.config_data["CBM"]["LAST"]) + 1
    
    def get_next_twic_nr(self):
        return int(self.config_data["TWIC"]["LAST"]) + 1
    
    def get_twic_attempts(self):
        return int(self.config_data["TWIC"]["ATTEMPTS"])

    def get_cbm_dir(self, cbm_nr = 0):
        if cbm_nr == 0:
            cbm_nr = self.get_next_cbm_nr()
        return "CBM " + str(cbm_nr)
    
    def get_start_filename(self):
        return self.START_FILENAME_PATTERN.replace("xxx", str(self.get_next_cbm_nr()))
    
    def get_test_filename(self):
        return os.path.join(self.get_cdrom_path(), self.get_start_filename())

    def testfile_exists(self):
        return os.path.exists(self.get_test_filename())
    
    def get_new_archive_dir(self, cbm_nr = 0):
        return os.path.join(self.get_cbm_archive_path(), self.get_cbm_dir(cbm_nr))

    def get_new_import_dir(self, cbm_nr = 0):
        return os.path.join(self.get_cbm_import_path(), self.get_cbm_dir(cbm_nr))

    def get_cbm_pattern(self, cbm_nr = 0):
        if cbm_nr == 0:
            pattern = "*" + str(self.get_next_cbm_nr()) + "*.*"
        else:
            pattern = "*" + str(self.get_next_cbm_nr()) + "*.*"
        return pattern
    
    def copy_to_import(self, cbm_nr = 0):
        source = self.get_new_archive_dir(cbm_nr)
        destination = self.get_new_import_dir(cbm_nr)
        shutil.copytree(source, destination)
        self.set_dir_to_777(destination)
        self.walk_directory_and_cleanup(destination, self.get_cbm_pattern(cbm_nr), keep = True)
        for pattern in self.config_data["DEL_PATTERN"]["IMPORT"]:
            self.walk_directory_and_cleanup(destination, pattern, keep = False)

    def reimport_cbm(self, start, end):
        for i in range(start, end+1):
            self.copy_to_import(cbm_nr = i)

    def copy_cbm(self):
        if self.testfile_exists():
            source = self.get_cdrom_path()
            destination = self.get_new_archive_dir()
            shutil.copytree(source, destination)
            self.set_dir_to_777(destination)
            for pattern in self.config_data["DEL_PATTERN"]["ARCHIVE"]:
                self.walk_directory_and_cleanup(destination, pattern, keep = False)
            self.copy_to_import()
        
    def del_file(self, path, filename):
        file_path = os.path.join(path, filename)
        os.remove(file_path)

    def walk_directory_and_cleanup(self, path, pattern, keep = False):
        for root, _, files in os.walk(path):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    if not keep:
                        #print(f"Del (not keep): {filename}, {pattern}")
                        self.del_file(root, filename)
                else:
                    if keep:
                        #print(f"Del (keep): {filename}, {pattern}")
                        self.del_file(root, filename)

    def set_dir_to_777(self, dir):
        mode = 0o777
        os.chmod(dir, mode)
#        try:
#            subprocess.run(["icacls", dir, "/grant", "Everyone:(OI)(CI)(F)"], check=True)
#            print(f"Permissions set to 777 for '{dir}' successfully.")
#        except subprocess.CalledProcessError as e:
#            print(f"Error setting permissions: {e}")