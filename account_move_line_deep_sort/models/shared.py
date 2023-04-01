from odoo import models

string_types = ["char", "text", "date", "datetime", "selection"]


def resolve_account_move_line_subfields(obj, line_order):
    if not line_order:
        return None
    val = getattr(obj, line_order.name)
    # Odoo object
    if isinstance(val, models.BaseModel):
        if not val:
            val = ""
        elif hasattr(val[0], "name"):
            val = ",".join(val.mapped("name"))
        else:
            val = ",".join([str(id) for id in val.mapped("id")])

    elif line_order.ttype in string_types:
        if not val:
            val = ""
        elif not isinstance(val, str):
            try:
                val = str(val)
            except Exception:
                val = ""
    return val
