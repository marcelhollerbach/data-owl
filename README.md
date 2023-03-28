# Data-Owl

The Data-Owl is a data catalogue. In this tool you can enlist your data and sort your data according to types.
Each registered data entry gets a unique identifier.
Each data entry can be of a specific type. The different types can be managed within the data-owl as well.

# Data Entries

Data entries consist of an id, name, description and state.
A readonly type called Meta-Data is also attached automatically. This explains who changed the entry as last.
Every other type needs to be manually attached and the fields fulfilled.

# Data Types

You can manage the different data types on your own in the data-owl.
Each data type can have multiple versions.
A data type version consists of different fields. Each field has a data type like a simple string, a name, and a
description.
The name and description is displayed in the UI.
When changes to the data type are done that are not backwards compatible, a new version is created.
When a new version of a data type is created, each data entry that uses this type needs to update its fields.

# Searching

In the searching module there is the concept of filters. A filter minimizes an existing set of entries.
Returned are only those entries that are passing every filter that is specified in a single search request.

For filters there are:
- `contains:` This simply checks if the passed text is part of some field of the data entry
- `type:` This checks if a entry fulfills a specific type.