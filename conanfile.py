import glob
import os

from conans import CMake, ConanFile, tools


class OctomapConan(ConanFile):
    name = "octomap"
    version = "1.9.0"
    description = (
        "An Efficient Probabilistic 3D Mapping Framework Based on Octrees."
        " Contains the main OctoMap library, the viewer octovis, and dynamicEDT3D."
    )
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("datastructure", "mapping")
    url = "https://github.com/rhololkeolke/conan-octomap"
    homepage = "http://octomap.github.io/"
    author = "Devin Schwab <dschwab@andrew.cmu.edu>"
    license = (
        "BSD-3-Clause"
    )  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md"]  # Packages the license for the
    # conanfile.py
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/OctoMap/octomap"
        tools.get(
            "{0}/archive/v{1}.tar.gz".format(source_url, self.version),
            sha256="5f81c9a8cbc9526b2e725251cd3a829e5222a28201b394314002146d8b9214dd",
        )
        extracted_dir = self.name + "-" + self.version

        # Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["BUILD_OCTOVIS_SUBPROJECT"] = False
        cmake.definitions["BUILD_DYNAMICETD3D_SUBPROJECT"] = False
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure(
            build_folder=self._build_subfolder, source_folder=self._source_subfolder
        )
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

        include_folder = os.path.join(self._source_subfolder, "octomap", "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        if self.options.shared:
            self.copy(pattern="*.so*", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
