#!/bin/bash
echo "* Extracting image"

export TMPDIR=`mktemp -d /tmp/selfextract.XXXXXX`

ARCHIVE=`awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' $0`

tail -n+$ARCHIVE $0 | tar xz -C $TMPDIR

CDIR=`pwd`
cd $TMPDIR
./installer.sh $@
SETUP_RESULT=$?

cd $CDIR
rm -rf $TMPDIR

exit $SETUP_RESULT

__ARCHIVE_BELOW__
