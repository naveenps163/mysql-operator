#!/bin/bash
# Copyright (c) 2023, Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#
# the job is triggered by gerrit events
# then triggers a build in a related pipeline for specified gerrit patchset revision
set -vx

source $WORKSPACE/tests/ci/jobs/auxiliary/set-env.sh || exit 10

echo "GIT_COMMIT: ${GIT_COMMIT}"
echo "GIT_COMMITTER_NAME: ${GIT_COMMITTER_NAME}"
echo "GIT_COMMITTER_EMAIL: ${GIT_COMMITTER_EMAIL}"
echo "GIT_URL: ${GIT_URL}"
echo "GIT_URL_N: ${GIT_URL_N}"
echo "GIT_BRANCH: ${GIT_BRANCH}"
echo "GIT_LOCAL_BRANCH: ${GIT_LOCAL_BRANCH}"
echo "GIT_PREVIOUS_COMMIT: ${GIT_PREVIOUS_COMMIT}"
echo "GIT_PREVIOUS_SUCCESSFUL_COMMIT: ${GIT_PREVIOUS_SUCCESSFUL_COMMIT}"

echo "GERRIT_PROJECT: ${GERRIT_PROJECT}"
echo "GERRIT_EVENT_TYPE: ${GERRIT_EVENT_TYPE}"
echo "GERRIT_EVENT_HASH: ${GERRIT_EVENT_HASH}"
echo "GERRIT_EVENT_ACCOUNT: ${GERRIT_EVENT_ACCOUNT}"
echo "GERRIT_EVENT_ACCOUNT_NAME: ${GERRIT_EVENT_ACCOUNT_NAME}"
echo "GERRIT_EVENT_ACCOUNT_EMAIL: ${GERRIT_EVENT_ACCOUNT_EMAIL}"
echo "GERRIT_NAME: ${GERRIT_NAME}"
echo "GERRIT_HOST: ${GERRIT_HOST}"
echo "GERRIT_PORT: ${GERRIT_PORT}"
echo "GERRIT_SCHEME: ${GERRIT_SCHEME}"
echo "GERRIT_VERSION: ${GERRIT_VERSION}"
echo "GERRIT_CHANGE_ID: ${GERRIT_CHANGE_ID}"
echo "GERRIT_CHANGE_SUBJECT: ${GERRIT_CHANGE_SUBJECT}"
echo "GERRIT_CHANGE_COMMIT_MESSAGE: ${GERRIT_CHANGE_COMMIT_MESSAGE}"
echo "GERRIT_CHANGE_NUMBER: ${GERRIT_CHANGE_NUMBER}"
echo "GERRIT_CHANGE_URL: ${GERRIT_CHANGE_URL}"
echo "GERRIT_PATCHSET_NUMBER: ${GERRIT_PATCHSET_NUMBER}"
echo "GERRIT_PATCHSET_REVISION: ${GERRIT_PATCHSET_REVISION}"
echo "GERRIT_BRANCH: ${GERRIT_BRANCH}"
echo "GERRIT_TOPIC: ${GERRIT_TOPIC}"
echo "GERRIT_REFSPEC: ${GERRIT_REFSPEC}"
echo "GERRIT_CHANGE_OWNER: ${GERRIT_CHANGE_OWNER}"
echo "GERRIT_CHANGE_OWNER_NAME: ${GERRIT_CHANGE_OWNER_NAME}"
echo "GERRIT_CHANGE_OWNER_EMAIL: ${GERRIT_CHANGE_OWNER_EMAIL}"
echo "GERRIT_PATCHSET_UPLOADER: ${GERRIT_PATCHSET_UPLOADER}"
echo "GERRIT_PATCHSET_UPLOADER_NAME: ${GERRIT_PATCHSET_UPLOADER_NAME}"
echo "GERRIT_PATCHSET_UPLOADER_EMAIL: ${GERRIT_PATCHSET_UPLOADER_EMAIL}"
echo "GERRIT_PATCHSET_ABANDONER: ${GERRIT_PATCHSET_ABANDONER}"
echo "GERRIT_PATCHSET_ABANDONER_NAME: ${GERRIT_PATCHSET_ABANDONER_NAME}"
echo "GERRIT_PATCHSET_ABANDONER_EMAIL: ${GERRIT_PATCHSET_ABANDONER_EMAIL}"
echo "GERRIT_PATCHSET_RESTORER: ${GERRIT_PATCHSET_RESTORER}"
echo "GERRIT_PATCHSET_RESTORER_NAME: ${GERRIT_PATCHSET_RESTORER_NAME}"
echo "GERRIT_PATCHSET_RESTORER_EMAIL: ${GERRIT_PATCHSET_RESTORER_EMAIL}"
echo "GERRIT_NEWREV: ${GERRIT_NEWREV}"
echo "GERRIT_EVENT_COMMENT_TEXT: ${GERRIT_EVENT_COMMENT_TEXT}"
echo "GERRIT_REFNAME: ${GERRIT_REFNAME}"
echo "GERRIT_OLDREV: ${GERRIT_OLDREV}"
echo "GERRIT_NEWREV: ${GERRIT_NEWREV}"


PIPELINE_NAME="dev"

OPERATOR_GIT_REPO_URL=$GERRIT_GIT_REPO_URL
OPERATOR_GIT_REPO_NAME=gerrit
OPERATOR_GIT_REVISION=$GERRIT_PATCHSET_REVISION
OPERATOR_GIT_REFSPEC=$GERRIT_REFSPEC
OPERATOR_DEV_IMAGE_TAG=$OPERATOR_BASE_VERSION_TAG-$GERRIT_EVENT_HASH-$GERRIT_CHANGE_NUMBER-$GERRIT_PATCHSET_NUMBER-'gerrit'
OPERATOR_IMAGE=$LOCAL_REGISTRY_ADDRESS/$LOCAL_REPOSITORY_NAME/$COMMUNITY_OPERATOR_IMAGE_NAME:$OPERATOR_DEV_IMAGE_TAG
OPERATOR_ENTERPRISE_IMAGE=$LOCAL_REGISTRY_ADDRESS/$LOCAL_REPOSITORY_NAME/$ENTERPRISE_OPERATOR_IMAGE_NAME:$OPERATOR_DEV_IMAGE_TAG
OPERATOR_TRIGGERED_BY=gerrit
OPERATOR_BUILD_IMAGES='true'

TRIGGERS_DIR=$WORKSPACE/triggers
if [[ ! -d $TRIGGERS_DIR ]]; then
    mkdir -p $TRIGGERS_DIR
fi
JOB_PARAMS_FILE=$TRIGGERS_DIR/trigger-$BUILD_NUMBER.txt

cat > $JOB_PARAMS_FILE<< EOF
OPERATOR_GIT_REPO_URL=${OPERATOR_GIT_REPO_URL}
OPERATOR_GIT_REPO_NAME=${OPERATOR_GIT_REPO_NAME}
OPERATOR_GIT_REVISION=${OPERATOR_GIT_REVISION}
OPERATOR_GIT_REFSPEC=${OPERATOR_GIT_REFSPEC}
OPERATOR_IMAGE=${OPERATOR_IMAGE}
OPERATOR_ENTERPRISE_IMAGE=${OPERATOR_ENTERPRISE_IMAGE}
OPERATOR_TRIGGERED_BY=${OPERATOR_TRIGGERED_BY}
OPERATOR_BUILD_IMAGES=${OPERATOR_BUILD_IMAGES}
OPERATOR_GERRIT_CHANGE_URL=${GERRIT_CHANGE_URL}
OPERATOR_GERRIT_TOPIC=${GERRIT_TOPIC}
OPERATOR_GERRIT_CHANGE_NUMBER=${GERRIT_CHANGE_NUMBER}
OPERATOR_GERRIT_PATCHSET_NUMBER=${GERRIT_PATCHSET_NUMBER}
OPERATOR_GERRIT_CHANGE_ID=${GERRIT_CHANGE_ID}
EOF
