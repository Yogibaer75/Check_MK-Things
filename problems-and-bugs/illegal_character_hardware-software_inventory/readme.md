# JSON example of illegal output of hardware-software inventory

This example shows a portion of hardware-software inventory output which has the
illegal characters `[` and `]` included inside a string object.

```
u' -[UUID', u'856941768EB811DE8418001A64DEA8E4]-'
```
This should be only one string for serial number and no list of two.

Normally every output must be cleared of illegal characters.
