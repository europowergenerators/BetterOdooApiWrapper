import xmlrpc.client
from typing import Any, Dict, List
import difflib

def set_nested_value(data_dict: Dict, field_path: str, value: Any):
    """Set a value in a nested dictionary given a field path (with slashes)."""
    keys = field_path.split("/")
    for key in keys[:-1]:
        data_dict = data_dict.setdefault(key, {})
    data_dict[keys[-1]] = value


def map_field(field: str) -> str:
    """Map 'id' to '.id' and 'external_id' to 'id' in field paths."""
    mapping = {"id": ".id", "external_id": "id"}
    return "/".join(mapping.get(part, part) for part in field.split("/"))


def unmap_field(field: str) -> str:
    """Reverse the mapping applied in map_field."""
    reverse_mapping = {".id": "id", "id": "external_id"}
    return "/".join(reverse_mapping.get(part, part) for part in field.split("/"))


class FieldProxy:
    def __init__(self, field_name: str, model: "ModelProxy", fields: Dict, field_path: str = None, export_field_path: str = None):
        self.field_name = field_name
        self.model = model
        self.fields = fields
        self.field_path = field_path or field_name
        self.export_field_path = export_field_path or field_name

        field_def = self.fields.get(self.field_name)
        self.is_relational = field_def and field_def.get("type") in {"many2one", "one2many", "many2many"}
        self.accessed_nested_field = False

    def __getattr__(self, attr: str) -> "FieldProxy":
        """Handle attribute access for relational fields."""
        field_def = self.fields.get(self.field_name)
        if not field_def:
            closest_matches = difflib.get_close_matches(self.field_name, self.fields.keys())
            if closest_matches:
                raise AttributeError(f"Field '{self.field_name}' not found. Try one of the following '{','.join(closest_matches)}'")
            else:
                raise AttributeError(f"Field '{self.field_name}' not found.")

        if field_def.get("type") in {"many2one", "one2many", "many2many"}:
            relation = field_def.get("relation")
            if not relation:
                raise AttributeError(f"'{self.field_name}' has no relation. This indicates an issue with your odoo database, contact your odoo administrator.")

            if relation not in self.model.query.orm.fields_cache:
                self.model.query.orm.fields_cache[relation] = self.model.query.orm._introspect_fields(relation)
            related_fields = self.model.query.orm.fields_cache[relation]

            # Allow 'id' and 'external_id' even if they are not in related_fields
            if attr not in related_fields and attr not in {"id", "external_id"}:
                closest_matches = difflib.get_close_matches(attr, related_fields.keys())
                if closest_matches:
                    raise AttributeError(f"Field '{attr}' not found in '{relation}'. Try one of the following '{','.join(closest_matches)}'")
                else:
                    raise AttributeError(f"Field '{attr}' not found in '{relation}'")

            self.accessed_nested_field = True

            return FieldProxy(
                field_name=attr,
                model=self.model,
                fields=related_fields,
                field_path=f"{self.field_path}.{attr}",
                export_field_path=f"{self.export_field_path}/{attr}",
            )
        else:
            raise AttributeError(f"'{self.field_name}' has no attributes. Remove '.{attr}'")


    def __eq__(self, other: Any):
        self.model._register_condition((self.field_path, "=", other))
        
    def __ne__(self, other: Any):
        self.model._register_condition((self.field_path, "!=", other))

    def __contains__(self, other: Any):
        operator = "ilike" if isinstance(other, str) else "in"
        value = other if isinstance(other, str) else ([other] if not isinstance(other, list) else other)
        self.model._register_condition((self.field_path, operator, value))

    def __lt__(self, other: Any):
        self.model._register_condition((self.field_path, "<", other))

    def __le__(self, other: Any):
        self.model._register_condition((self.field_path, "<=", other))

    def __gt__(self, other: Any):
        self.model._register_condition((self.field_path, ">", other))

    def __ge__(self, other: Any):
        self.model._register_condition((self.field_path, ">=", other))


class ModelProxy:
    def __init__(self, fields: Dict, query: "OdooQuery"):
        self.fields = fields
        self.query = query
        self.conditions = []
        self.accesses = []

    def __getattr__(self, item: str) -> FieldProxy:
        """Handle attribute access to dynamically return a FieldProxy."""
        if item in self.fields or item in {"id", "external_id"}:
            self.accesses.append(item)

            return FieldProxy(
                field_name=item,
                model=self,
                fields=self.fields,
                field_path=item,
                export_field_path=item,
            )
        else:
            closest_matches = difflib.get_close_matches(item, self.fields.keys())
            if closest_matches:
                raise AttributeError(f"Field '{item}' not found. Try one of the following '{','.join(closest_matches)}'")
            else:
                raise AttributeError(f"Field '{item}' not found.")

    def _register_condition(self, condition: tuple):
        """Register a filter condition."""
        self.conditions.append(condition)


class Client:
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        # Initialize ServerProxy instances
        self.common_proxy = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)
        self.object_proxy = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)
        self.uid = self._authenticate()
        self.fields_cache = {}
        self.context = {}

    def _authenticate(self) -> int:
        return self.common_proxy.authenticate(self.db, self.username, self.password, {})

    def __getitem__(self, model_name: str) -> "OdooQuery":
        if model_name not in self.fields_cache:
            self.fields_cache[model_name] = self._introspect_fields(model_name)
        return OdooQuery(self, model_name)

    def _introspect_fields(self, model_name: str) -> Dict:
        """Fetch field metadata for the given model."""
        return self.object_proxy.execute_kw(
            self.db,
            self.uid,
            self.password,
            model_name,
            "fields_get",
            [],
            {"attributes": ["string", "help", "type", "relation"], "context": self.context},
        )

    def set_context(self, **kwargs):
        """Set the context for subsequent queries."""
        self.context.update(kwargs)
        

class OdooQuery:
    def __init__(self, orm: Client, model_name: str):
        self.orm = orm
        self.model_name = model_name
        self.projections: List[FieldProxy] = []
        self.filters: List[tuple] = []
        self.order: List[tuple] = []
        self.limit = None
        self.fields = orm.fields_cache[model_name]
        self.ids = []
        self.context = orm.context.copy()

    def select(self, select_func) -> "OdooQuery":
        """Apply a projection."""
        proxy = ModelProxy(self.fields, self)
        result = select_func(proxy)

        def collect_projections(res) -> List[FieldProxy]:
            if isinstance(res, FieldProxy):
                return [res]
            elif isinstance(res, (list, tuple)):
                projections = []
                for item in res:
                    projections.extend(collect_projections(item))
                return projections
            return []

        projections = collect_projections(result)
        # Remove duplicates based on export_field_path
        self.projections = list({fp.export_field_path: fp for fp in projections}.values())
        return self

    def filter(self, filter_func) -> "OdooQuery":
        """Apply filter conditions using a lambda function."""
        proxy = ModelProxy(self.fields, self)
        filter_func(proxy)
        self.filters.extend(proxy.conditions)
        return self

    def order_by(self, order_func, descending: bool = False) -> "OdooQuery":
        """Apply ordering on fields."""
        proxy = ModelProxy(self.fields, self)
        result = order_func(proxy)

        def collect_fields(res) -> List[FieldProxy]:
            if isinstance(res, FieldProxy):
                return [res]
            elif isinstance(res, (list, tuple)):
                fields = []
                for item in res:
                    fields.extend(collect_fields(item))
                return fields
            return []

        direction = "desc" if descending else "asc"
        for fp in collect_fields(result):
            self.order.append((fp.field_path, direction))
        return self

    def order_by_descending(self, order_func) -> "OdooQuery":
        """Apply descending order on a field."""
        return self.order_by(order_func, descending=True)

    def external_ids(self, external_ids_list: List[str]) -> "OdooQuery":
        """Filter records by their external IDs."""
        names = [eid.split(".", 1)[1] for eid in external_ids_list]
        domain = [("name", "in", names)]
        ir_model_data = self.orm.object_proxy.execute_kw(
            self.orm.db,
            self.orm.uid,
            self.orm.password,
            "ir.model.data",
            "search_read",
            [domain],
            {"fields": ["res_id"], "context": self.context},
        )
        self.ids.extend([record["res_id"] for record in ir_model_data])
        return self

    def _prepare_domain(self) -> List[tuple]:
        domain = self.filters.copy()
        if self.ids:
            domain.append(("id", "in", self.ids))
        return domain
        

    def _prepare_fields(self) -> List[str]:
        return list(set(fp.field_path for fp in self.projections)) if self.projections else []

    def _prepare_order(self) -> str:
        return ", ".join(f"{field} {direction}" for field, direction in self.order) if self.order else ""

    def _extract_keys_from_list_of_dicts(self, list_of_dicts):
            keys = set()
            for dict in list_of_dicts:
                keys.update(dict.keys())

            return list(keys)
    
    def create(self, list_of_objects) -> List[int]:
        # Perform a check to see if all mandatory items are fulfilled
        # Field introspection cannot be used to check the required fields. because odoo enforces business logic at different levels.

        if type(list_of_objects) != list:
            raise TypeError
        
        keys = self._extract_keys_from_list_of_dicts(list_of_objects)
        missing_keys = [key for key in keys if key not in self.fields]
        if missing_keys:
            error_string = f"Some fields have not been found on the model '{self.model_name}':\n"
            for key in missing_keys:
                closest_matches = difflib.get_close_matches(key, self.fields.keys())
                if closest_matches:
                    error_string = error_string + f"- '{key}'. Perhaps you meant: '{','.join(closest_matches)}'\n"
                else:
                    error_string = error_string + f"- '{key}'.\n"
            raise AttributeError(error_string)


        ids = self.orm.object_proxy.execute_kw(
            self.orm.db,
            self.orm.uid,
            self.orm.password,
            self.model_name,
            'create',
            [list_of_objects],
        )
        if type(ids) == int:
            ids = [ids]
        self.ids.extend(ids)
        return self

    def get(self) -> List[Dict]:
        """Execute the query by manually fetching nested relational data."""
        domain = self._prepare_domain()

        # Build a nested structure of fields to fetch
        def build_nested_fields_structure(projections: List[FieldProxy]) -> Dict:
            nested_fields = {}
            for fp in projections:
                path = fp.field_path.split('.')
                current_level = nested_fields
                for part in path:
                    current_level = current_level.setdefault(part, {})
            return nested_fields

        nested_fields = build_nested_fields_structure(self.projections)

        def fetch_records(model_name: str, ids: List[int], fields_structure: Dict) -> Dict[int, Dict]:
            if not ids:
                return {}
            field_defs = self.orm.fields_cache.setdefault(
                model_name, self.orm._introspect_fields(model_name)
            )
            fields_to_fetch = list(fields_structure.keys())
            relational_fields = {
                field_name: {
                    'relation': field_defs[field_name]['relation'],
                    'type': field_defs[field_name]['type'],
                    'nested_fields': nested_fields
                }
                for field_name, nested_fields in fields_structure.items()
                if field_defs[field_name]['type'] in {'many2one', 'one2many', 'many2many'}
            }

            # Ensure 'id' is included
            if 'id' not in fields_to_fetch:
                fields_to_fetch.append('id')

            # Fetch records at this level
            records = self.orm.object_proxy.execute_kw(
                self.orm.db,
                self.orm.uid,
                self.orm.password,
                model_name,
                'read',
                [ids],
                {'fields': fields_to_fetch, 'context': self.context}
            )

            records_by_id = {record['id']: record for record in records}

            # Recursively fetch related records
            for field_name, rel_info in relational_fields.items():
                related_ids = set()
                field_type = rel_info['type']
                for record in records:
                    if field_type == 'many2one':
                        rel_data = record.get(field_name)
                        if rel_data:
                            rel_id = rel_data[0] if isinstance(rel_data, (list, tuple)) else rel_data
                            related_ids.add(rel_id)
                    else:  # 'one2many' or 'many2many'
                        rel_ids = record.get(field_name, [])
                        related_ids.update(rel_ids)

                related_records = fetch_records(
                    rel_info['relation'],
                    list(related_ids),
                    rel_info['nested_fields']
                )

                # Map related data back to parent records
                for record in records:
                    if field_type == 'many2one':
                        rel_data = record.get(field_name)
                        if rel_data:
                            rel_id = rel_data[0] if isinstance(rel_data, (list, tuple)) else rel_data
                            record[field_name] = related_records.get(rel_id, {})
                    else:  # 'one2many' or 'many2many'
                        rel_ids = record.get(field_name, [])
                        record[field_name] = [related_records.get(rel_id, {}) for rel_id in rel_ids]

            return records_by_id

        # Fetch main record IDs
        main_ids = self.orm.object_proxy.execute_kw(
            self.orm.db,
            self.orm.uid,
            self.orm.password,
            self.model_name,
            'search',
            [domain],
            {'limit': self.limit, 'order': self._prepare_order(), 'context': self.context}
        )

        if not main_ids:
            return []

        # Fetch records with nested fields
        records_by_id = fetch_records(self.model_name, main_ids, nested_fields)

        # Return records as a list, preserving order
        return [records_by_id[record_id] for record_id in main_ids]

    def export(self) -> List[Dict]:
        """Execute the query using export_data."""
        for fp in self.projections:
            if fp.is_relational and not fp.accessed_nested_field:
                raise ValueError(
                    f"Cannot select relational field '{fp.field_name}' without specifying a nested field in export. Did you mean: '{fp.field_name}.id'?"
                )

        domain = self._prepare_domain()
        fields = [map_field(fp.export_field_path) for fp in self.projections]
        fields = list(dict.fromkeys(fields))  # Remove duplicates while preserving order
        ids = self.orm.object_proxy.execute_kw(
            self.orm.db,
            self.orm.uid,
            self.orm.password,
            self.model_name,
            "search",
            [domain],
            {"limit": self.limit, "context": self.context},
        )

        if not ids:
            return []

        result = self.orm.object_proxy.execute_kw(
            self.orm.db,
            self.orm.uid,
            self.orm.password,
            self.model_name,
            "export_data",
            [ids, fields],
            {"context": self.context},
        )

        data = result.get("datas", [])
        records = []
        for row in data:
            record = {}
            for field_name, value in zip(fields, row):
                key = unmap_field(field_name)
                set_nested_value(record, key, value)
            records.append(record)

        return records

    def take(self, limit: int) -> "OdooQuery":
        """Set a limit on the number of records to fetch."""
        self.limit = limit
        return self

    def first(self) -> Dict:
        """Get the first record matching the query."""
        self.limit = 1
        results = self.get()
        return results[0] if results else None
