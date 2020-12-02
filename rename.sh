#!/bin/bash

if [ $1 ]; then
    neworg=$1
else
    echo "new git organization name or username not supplied"
    exit 1;
fi


if [ $2 ]; then
    newrepo=$2
else
    echo "new repo name not supplied"
    exit 1;
fi


if [ "$3" ]; then
    licensor=$3
else
    echo "licensor not supplied"
    exit 1;
fi


#replace "template_pypi" with the new repo name in every file
for f in *; do sed -i.bak "s/template_pypi/${newrepo}/g" "${f}"; done
for f in *; do sed -i.bak "s/myorg/${neworg}/g" "${f}"; done
for f in *; do sed -i.bak "s/John Doe/${licensor}/g" "${f}"; done
rm *.bak


#set today
today=$(date +%Y-%m-%d)
sed -i.bak "s/1970-01-01/${today}/g" CHANGES.md
rm CHANGES.md.bak 


#set year
year=$(date +%Y)
sed -i.bak "s/1970/${year}/g" LICENSE
rm LICENSE.bak 


#rename module folder
mv template_pypi "${newrepo}"


#reinitialize git
rm -rf .git
git init

#self-destruction
rm -- "$0"