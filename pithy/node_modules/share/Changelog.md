# ShareJS Changelog 0.6 -> 0.7

- Moved everything into collections
- Create and delete are now document operations
- Text API 'delete' callback tells you the position and length, not the position and deleted text.
- Types no longer guarantee that `apply` preserves the old document object. This is good for performance, but bad for lots of other reasons.
- `on 'remoteop'` and `on 'changed'` document events have been replaced with `on 'op'`. It is called with `(op, context)`. By default, context is truthy for local edits and false for remote edits.
- Document editing contexts have been added. Simply call doc
- Added an `on 'before op'` emitter to allow the inspection of snapshots before operations edit them.

- Connections aren't assumed, and aren't provided by default.
- You can't submit an op to the client at an old version. As a result, the client no longer caches all operations its ever seen.

- Microevent is no longer chainable (foo.on('hi', function(){}).on(…).emit('hi') ) in order to make it compatible with NodeJS's event emitter.

- Documents are editable before they have a snapshot. This allows you to create new documents and set their content without consulting the server.
- Documents can submit operations to the server while unsubscribed. The document will be brought up to date as each operation is sent to the server.
- Queries have been added. You can make a fetch query or a subscribed query. Fetch queries basically just forward a mongo (or whatever) query to the database. Subscribe queries re-poll as data is edited.

- The entire client has been rewritten in javascript.