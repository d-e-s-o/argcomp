# Makefile

#/***************************************************************************
# *   Copyright (C) 2016-2017 Daniel Mueller (deso@posteo.net)              *
# *                                                                         *
# *   This program is free software: you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation, either version 3 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU General Public License for more details.                          *
# *                                                                         *
# *   You should have received a copy of the GNU General Public License     *
# *   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
# ***************************************************************************/

ROOT := $(shell pwd)/..
PYTHONPATH := "$(ROOT)/argcomp/src/:${PYTHONPATH}"


.PHONY: all
all: test testSetup


.PHONY: test
test:
	@PYTHONPATH=$(PYTHONPATH)\
	 PYTHONDONTWRITEBYTECODE=1\
	  python -m unittest --verbose deso.argcomp.test.allTests


.PHONY: %
%:
	@echo "Running deso.argcomp.test.testCompletingArgumentParser.$@ ..."
	@PYTHONPATH=$(PYTHONPATH)\
	 PYTHONDONTWRITEBYTECODE=1\
	  python -m unittest --verbose deso.argcomp.test.testCompletingArgumentParser.$@


# The testing procedure is quite involved. First, we clone this
# repository (required so that we do not pollute the local structure
# but also to make sure no uncommitted files are present that could
# potentially get picked up during the packaging phase). Next we apply
# potential changes to existing files made locally. This step helps
# during development. Note that untracked files are not picked up by
# design.
# We then create a source distribution (which is the only distribution
# form we are interested in). We extract this distribution into another
# directory. There we check for the relevant setup.py related commands
# to work and run the test suite.
# Lastly, we properly install the source distribution and make sure the
# module is actually importable.
# As an aside, easy_install is part of setuptools so we do not have an
# additional dependency (we require setuptools anyway). Note that
# instead of easy_install we could also use python setup.py install_lib
# --install-dir=<...> which is equally hacky (requiring path globbing)
# but less likely reflects how users will install the package.
.PHONY: testSetup
testSetup: SETUP_PY := bin/python setup.py --no-user-cfg --quiet
testSetup: INSTALL := bin/easy_install --quiet
testSetup:
	@( \
	  DIST_DIR="$$(mktemp --directory)" && \
	  git clone --quiet "$(ROOT)" "$${DIST_DIR}" && \
	  pushd "$${DIST_DIR}/argcomp" > /dev/null && \
	    python -m venv --symlinks . && \
	    source bin/activate && \
	    ( \
	      git -C "$(ROOT)" diff --exit-code --no-prefix --no-color --binary --full-index HEAD && \
	      echo -e "diff --git __ __\nnew file mode 100644\nindex 000000..000000" \
	    ) | git apply -p0 --binary --index && \
	    $(SETUP_PY) sdist --format=gztar --dist-dir=distribute && \
	    PACKAGE="$$(echo $${PWD}/distribute/argcompd-*)" && \
	    popd > /dev/null && \
	  TEST_DIR="$$(mktemp --directory)" && \
	  pushd "$${TEST_DIR}" > /dev/null && \
	    tar --extract --gzip --file="$${PACKAGE}" && \
	    cd argcompd-* && \
	    python -m venv --symlinks . && \
	    source bin/activate && \
	    $(SETUP_PY) --name > /dev/null && \
	    $(SETUP_PY) --version > /dev/null && \
	    $(SETUP_PY) --description > /dev/null && \
	    $(SETUP_PY) --long-description > /dev/null && \
	    PYTHONPATH="$${PWD}/src/" $(SETUP_PY) test && \
	    popd > /dev/null && \
	  rm -fr "$${TEST_DIR}" && \
	  INSTALL_DIR="$$(mktemp --directory)" && \
	  pushd "$${INSTALL_DIR}" > /dev/null && \
	    python -m venv --symlinks . && \
	    source bin/activate && \
	    PYTHONPATH=$$(echo lib/*/site-packages/) $(INSTALL) --prefix=. "$${PACKAGE}" && \
	    python -c "import deso.argcomp" && \
	    popd > /dev/null && \
	  rm -fr "$${INSTALL_DIR}" && \
	  rm -fr "$${DIST_DIR}" \
	)


# Note that we intentionally specify the input format as 'markdown' and
# not 'markdown_github' as the latter screws up the output.
README.rst: README.md
	@pandoc --from=markdown --to=rst $< --output=$@


.PHONY: doc
doc: README.rst


.PHONY: upload
upload: doc
	@git diff --exit-code --quiet --no-patch
	@python setup.py sdist upload \
	  --sign --identity=deso@posteo.net \
	  --repository https://pypi.python.org/pypi
