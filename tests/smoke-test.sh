#!/bin/bash

# Fail if any command returns non-zero
# Show executed commands
set -e -x

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER="${SERVER:-http://localhost:8888/v1}"

AUTH="${AUTH:-user:pass}"
EDITOR_AUTH="${EDITOR_AUTH:-editor:pass}"
REVIEWER_AUTH="${REVIEWER_AUTH:-reviewer:pass}"

# Create Kinto accounts
echo '{"data": {"password": "pass"}}' | http --check-status PUT $SERVER/accounts/user
echo '{"data": {"password": "pass"}}' | http --check-status PUT $SERVER/accounts/editor
echo '{"data": {"password": "pass"}}' | http --check-status PUT $SERVER/accounts/reviewer

http --check-status $SERVER/__heartbeat__
http --check-status $SERVER/__api__ | grep "/buckets/monitor/collections/changes/records"

#
# Basic test
#

http --check-status PUT $SERVER/buckets/blog --auth $AUTH
http --check-status PUT $SERVER/buckets/blog/collections/articles --auth $AUTH
# kinto-attachment test
# New record.
http --check-status --form POST $SERVER/buckets/blog/collections/articles/records/80ec9929-6896-4022-8443-3da4f5353f47/attachment attachment@kinto-logo.svg --auth $AUTH
# Existing record.
echo '{"data": {"type": "logo"}}' | http --check-status PUT $SERVER/buckets/blog/collections/articles/records/logo --auth $AUTH
http --check-status --form POST $SERVER/buckets/blog/collections/articles/records/logo/attachment attachment@kinto-logo.svg --auth $AUTH

#
# kinto-signer test
#

python $DIR/e2e.py --server=$SERVER --auth=$AUTH --editor-auth=$EDITOR_AUTH --reviewer-auth=$REVIEWER_AUTH --source-bucket="source" --source-col="source"
python validate_signature.py --server=$SERVER --bucket=destination --collection=source

# kinto-changes
http --check-status $SERVER/buckets/monitor/collections/changes/records | grep '"destination"'

# kinto-admin
http --check-status -h "$SERVER/admin/"
http --check-status -h "$SERVER/admin/index.html"

# Empty history for preview and signed.
http --check-status GET $SERVER/buckets/preview/history --auth $AUTH | grep '\[\]'
http --check-status GET $SERVER/buckets/destination/history --auth $AUTH | grep '\[\]'

# END OF THE TEST
# If you made it here, that means all the smoke tests above did not fail.
# Party!
