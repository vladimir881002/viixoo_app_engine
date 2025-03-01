from typing import List, Tuple, Any

class DomainTranslator:
    TERM_OPERATORS_SQL = {
        '=': '=', '!=': '!=', '<=': '<=', '<': '<', '>': '>', '>=': '>=',
        'like': 'LIKE', 'not like': 'NOT LIKE',
        'ilike': 'ILIKE', 'not ilike': 'NOT ILIKE',
        'in': 'IN', 'not in': 'NOT IN',
        'child_of': 'IN', 'parent_of': 'IN',  # Hierarchical handling needed
        'startswith': 'LIKE', 'endswith': 'LIKE', 'contains': 'LIKE',
        'is null': 'IS NULL', 'is not null': 'IS NOT NULL',
        'any': 'ANY', 'not any': 'NOT ANY'
    }

    @staticmethod
    def translate(domain: List[Any]) -> str:
        if not domain:
            return "1=1", []        
        
        sql_conditions, params = DomainTranslator._parse_domain(domain)
        return f"WHERE {sql_conditions}", params
    
    @staticmethod
    def _parse_domain(domain: List[Any]) -> Tuple[str, List[Any]]:
        sql_conditions = []
        condition_counts = 0
        operator_found = False

        params = []
        stack = []
        
        def apply_stack():
            while stack:
                if len(sql_conditions) < 2 and stack[-1] in ('|', '&'):
                    break  # Ensure there are enough conditions to apply
                op = stack.pop()
                if op == '|':
                    if len(sql_conditions) == 2:
                        cond2 = sql_conditions.pop()
                        cond1 = sql_conditions.pop()
                        sql_conditions.append(f"({cond1} OR {cond2})")
                    elif len(sql_conditions) > 2:
                        cond2 = sql_conditions.pop()
                        cond1 = sql_conditions.pop()
                        if op == '|' and len(stack) > 0 and stack[-1] == '|':
                            sql_conditions.append(f"{cond1} OR {cond2}")
                        else:
                            sql_conditions.append(f"({cond1} OR {cond2})")
                elif op == '&':
                    if len(sql_conditions) == 2:
                        cond2 = sql_conditions.pop()
                        cond1 = sql_conditions.pop()
                        sql_conditions.append(f"({cond1} AND {cond2})")
                    elif len(sql_conditions) > 2:
                        cond2 = sql_conditions.pop()
                        cond1 = sql_conditions.pop()
                        if op == '&' and len(stack) > 0 and stack[-1] == '&':
                            sql_conditions.append(f"{cond1} AND {cond2}")
                        else:
                            sql_conditions.append(f"({cond1} AND {cond2})")
                elif op == '!':
                    if len(sql_conditions) >= 1:
                        cond = sql_conditions.pop()
                        sql_conditions.append(f"NOT ({cond})")
        
        for term in domain:
            if isinstance(term, str) and term in ('|', '&', '!'):
                stack.append(term)
                operator_found = True
            elif isinstance(term, (list, tuple)) and len(term) == 3:
                field, operator, value = term
                sql_operator = DomainTranslator.TERM_OPERATORS_SQL.get(operator, '=')
                
                if operator in ('in', 'not in') and isinstance(value, (list, tuple)):
                    placeholders = ', '.join(['%s'] * len(value))
                    condition = f"{field} {sql_operator} ({placeholders})"
                    params.extend(value)
                elif operator in ('like', 'not like', 'ilike', 'not ilike', 'startswith', 'endswith', 'contains'):
                    if operator == 'startswith':
                        value = f"{value}%"
                    elif operator == 'endswith':
                        value = f"%{value}"
                    elif operator == 'contains':
                        value = f"%{value}%"
                    condition = f"{field} {sql_operator} %s"
                    params.append(value)
                elif operator == 'child_of':
                    condition = f"{field} IN (SELECT id FROM some_table WHERE parent_id = %s)"
                    params.append(value)
                elif operator in ('is null', 'is not null'):
                    condition = f"{field} {sql_operator}"
                else:
                    condition = f"{field} {sql_operator} %s"
                    params.append(value)
                
                sql_conditions.append(condition)
                
                if operator_found:
                    condition_counts += 1
                    if len(sql_conditions) > 1 and condition_counts > len(stack):
                        operator_found = False
                        apply_stack()
        
        apply_stack()  # Ensure any remaining operations are applied
        return ' AND '.join(sql_conditions), params

# Example usage

if __name__ == '__main__':
    domain = [('name', 'like', 'John'), '|', ('age', '>', 30), ('city', '=', 'New York')]
    domain1 = [
        '!', '|', '|',
            ('name', '=', 'Jack'),
            ('name', '=', 'Sam'),
            ('name', '=', 'Daniel'),
    ]
    domain2 = [
            '&', '&',
                ('name', '!=', 'Jack'),
                ('name', '!=', 'Sam'),
                ('name', '!=', 'Daniel'),
        ]
    domain3 = [
        ('name', '!=', 'Jack'),
        ('name', '!=', 'Sam'),
        ('name', '!=', 'Daniel'),
    ]
    domain4 = [
        ('name', 'ilike', 'John'),
        ('age', '>=', 30),
        ('id', 'in', [1, 2, 3]),
        ('active', 'is not null', None),
        '|', ('name', 'like', 'Doe'), ('email', 'ilike', 'example.com'),
        '!', ('status', '=', 'inactive')
    ]
    translator = DomainTranslator()
    sql_query, params = translator.translate(domain)
    print('Domain:', domain, sql_query, params)
    
    sql_query, params = translator.translate(domain1)
    print('Domain:', domain1, sql_query, params)

    sql_query, params = translator.translate(domain2)
    print('Domain:', domain2, sql_query, params)

    sql_query, params = translator.translate(domain3)
    print('Domain:', domain3, sql_query, params)

    sql_query, params = translator.translate(domain4)
    print('Domain:', domain4, sql_query, params)
