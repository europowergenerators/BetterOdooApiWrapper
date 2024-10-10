# BetterOdooApiWrapper

A minimal Python ORM wrapper for the Odoo API.

## Overview

BetterOdooApiWrapper is a lightweight, Pythonic wrapper around the Odoo XML-RPC API, providing an ORM-like interface to interact with Odoo models and records. It simplifies the process of querying, filtering, and manipulating data in Odoo from Python applications.

## Features

- **Pythonic ORM Interface**: Interact with Odoo models using familiar Python syntax.
- **Dynamic Model Access**: Access any Odoo model dynamically without pre-defining classes.
- **Complex Querying**: Support for filtering, ordering, and selecting specific fields.
- **Relational Fields Handling**: Seamlessly work with `many2one`, `one2many`, and `many2many` fields.
- **Context Management**: Easily set and update the Odoo context for your queries.
- **Export Functionality**: Export data, including nested relational fields, efficiently.

## Getting Started

### Connecting to Odoo

```python
from wrapper import Client

# Initialize the Odoo client
odoo = Client(
    url="https://your-odoo-instance.com",
    db="your-database-name",
    username="your-username",
    password="your-password"
)
```

### Setting Context

Optionally, you can set the context for your operations:

```python
# Set the context for subsequent queries
odoo.set_context(lang='en_US', tz='UTC')
```

### Accessing Models

```python
# Access the 'res.partner' model
partners = odoo['res.partner']
```

## Querying Data

### Selecting Fields

```python
# Select specific fields
partners = partners.select(lambda p: (p.name, p.email))
```

### Filtering Data

```python
# Filter partners where name contains 'John' and email is not null
partners = partners.filter(lambda p: ('John' in p.name, p.email != False))
```

### Ordering Results

```python
# Order by name ascending
partners = partners.order_by(lambda p: p.name)

# Order by name descending
partners = partners.order_by_descending(lambda p: p.name)
```

### Limiting Results

```python
# Limit to first 10 records
partners = partners.take(10)
```

### Fetching the Data

```python
# Execute the query and get the results
results = partners.get()
```

### Fetching a Single Record

```python
# Get the first matching record
partner = partners.first()
```

## Working with Relational Fields

```python
# Select fields from related models
partners = partners.select(lambda p: (
    p.name,
    p.company_id.name,
    p.company_id.country_id.name
))
results = partners.get()
```

## Exporting Data

Use the `export` method to fetch data using Odoo's `export_data` method, which is efficient for large datasets.
> [!WARNING] 
> This implicitly creates external_ids for all returned records, including requested related records.

```python
# Export data including nested relational fields
data = partners.export()
```

## Filtering by External IDs

```python
# Filter records by their external IDs
partners = partners.external_ids(['module.partner_1', 'module.partner_2'])
results = partners.get()
```

## Full Example

```python
from odoopyorm import Client

# Initialize the client
odoo = Client(
    url="https://your-odoo-instance.com",
    db="your-database-name",
    username="your-username",
    password="your-password"
)

# Set context if needed
odoo.set_context(lang='en_US', tz='UTC')

# Build the query
partners = (
    odoo['res.partner']
    .select(lambda p: (
        p.name,
        p.email,
        p.company_id.name,
        p.company_id.country_id.name
    ))
    .filter(lambda p: (
        p.is_company == True,
        p.customer_rank > 0
    ))
    .order_by(lambda p: p.name)
    .take(50)
)

# Execute the query
results = partners.get()

# Close the client connection
odoo.close()

# Process the results
for partner in results:
    print(f"Name: {partner['name']}, Email: {partner['email']}")
    print(f"Company: {partner['company_id']['name']}")
    print(f"Country: {partner['company_id']['country_id']['name']}")
```

## Creating Records
You can create single or bulk records in odoo by supplying a list of key: value dictionaries.

```python
created_record = partners.create([{"name": "James Smith"}]).select(lambda x: x.name).get()
```
or simply
```python
created_ids = partners.create([{"name": "James Smith"}]).ids
```

## Deleting Records
Deleting records can be done in 3 ways.
You can either specify external_ids, database_ids, or use a filter like with search.

```python
partners.database_ids([1, 2, 3]).delete()
partners.external_ids(["external_id_1", "external_id_2"]).delete()
partners.filter(lambda x: x.name == "John Doe").delete()
```


## Roadmap
- Fix no filter returning only ID on get
- Cache Field introspection
- Generate python stub files from field introspection to introduce "dynamic" code completion
- Add Read Pagination support with easy itterations
- Add support for Delete
- Add support for Write
- Add support for Update


## Contributing

We are not open to pull requests. Create an issue to discuss pain points in the wrapper.

## Disclaimer

This project is not affiliated with or endorsed by Odoo S.A. It is an independent tool designed to facilitate interaction with the Odoo API.


---

Happy coding! 🚀
