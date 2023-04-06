# MIT License
#
# # Copyright (c) 2023 Saurabh Gupta, Ignacio Vizzo, Cyrill Stachniss, University of Bonn
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
include(ExternalProject)
include(GNUInstallDirs)

ExternalProject_Add(
  external_sophus
  PREFIX sophus
  # Uncomment after https://github.com/strasdat/Sophus/pull/502 gets merged
  # URL https://github.com/strasdat/Sophus/archive/refs/tags/1.22.10.tar.gz
  URL https://github.com/nachovizzo/Sophus/archive/refs/tags/1.22.11.tar.gz
  UPDATE_COMMAND ""
  CMAKE_ARGS -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR> -DBUILD_SOPHUS_EXAMPLES=OFF -DBUILD_SOPHUS_TESTS=OFF
             -DCMAKE_BUILD_TYPE=Release)

ExternalProject_Get_Property(external_sophus INSTALL_DIR)
add_library(SophusHelper INTERFACE)
add_dependencies(SophusHelper external_sophus)
target_compile_definitions(SophusHelper INTERFACE SOPHUS_USE_BASIC_LOGGING=1)
target_include_directories(SophusHelper SYSTEM INTERFACE ${INSTALL_DIR}/${CMAKE_INSTALL_INCLUDEDIR})
add_library(Sophus::Sophus ALIAS SophusHelper)
