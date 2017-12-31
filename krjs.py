import argparse
import copy
import os
import json
import sys
import traceback

print('Kings Raid Skill Dumper v1.0')
print('By: cpp (Reddit: u/cpp_is_king, Discord: @cpp#0120)')
print('Paypal: cppisking@gmail.com')
print()

if sys.version_info < (3,5):
    print('Error: This script requires Python 3.5 or higher.  Please visit '
          'www.python.org and install a newer version.')
    print('Press any key to exit...')
    input()
    sys.exit(1)

args = None
creature_by_index = None
creature_by_name = None
skills_by_index = None
skill_level_factors = None
indent_level = 0

def print_line(message):
    global indent_level
    print(' ' * indent_level, end = '')
    print(message)

def indent(amount):
    global indent_level
    indent_level = indent_level + amount

def decode_file(path):
    codecs = ['utf-8-sig', 'utf-8']
    for c in codecs:
        try:
            with open(path, 'r', encoding=c) as fp:
                return fp.read()
        except:
            traceback.print_exc()
            pass
    return None

def parse_args():
    parser = argparse.ArgumentParser(description='Kings Raid Json Dumper.')
    parser.add_argument('--json_path', type=str, help='The folder containing json files')
    parser.add_argument('--hero', type=str, help='Limit dumping to the specified hero (e.g. Kasel)')
    parser.add_argument('--books', type=str, help='Assume skills have the specified book upgrades (e.g. --books=1,3,2,1)')
    return parser.parse_args()

def max_numbered_key(obj, prefix):
    indices = set(map(lambda x : int(x[-1]),
                                filter(lambda x : x.startswith(prefix), obj.keys())))
    if len(indices) == 0:
        return None
    return max(indices)

def update_table(json_obj, indexes):
    for obj in json_obj:
        for key, table in indexes:
            value = obj[key]
            if value in table:
                print('Warning: {0}={1} appears more than once.  Ignoring subsequent occurrences...'.format(key, value))
                continue
            table[value] = obj

def load_creatures_table():
    print('Loading creatures...')
    global args
    global creature_by_index
    global creature_by_name

    path = os.path.join(args.json_path, 'CreatureTable.json')
    content = decode_file(path)
    json_obj = json.loads(content)
    creature_by_index = {}
    creature_by_name = {}
    update_table(json_obj, [('Index', creature_by_index), ('CodeName', creature_by_name)])

def load_skills_table():
    print('Loading skills...')
    global args
    global skills_by_index
    index = 0
    skills_by_index = {}
    path = os.path.join(args.json_path, 'SkillTable.json')
    while True:
        content = decode_file(path)
        json_obj = json.loads(content)
        update_table(json_obj, [('Index', skills_by_index)])
        index = index + 1
        path = os.path.join(args.json_path, 'SkillTable{0}.json'.format(index))
        if not os.path.exists(path):
            break

def generate_factors(obj):
    max_factor = max_numbered_key(obj, 'Factor')
    assert(max_factor is not None)

    result = {}
    for x in range(1, max_factor+1):
        key_name = 'Factor{0}'.format(x)
        if key_name in obj:
            result[x] = obj[key_name]
    return result

def load_skill_level_factors_table():
    print('Loading skill level factors...')
    global skill_level_factors

    skill_level_factors = {}
    path = os.path.join(args.json_path, 'SkillLevelFactorTable.json')
    content = decode_file(path)
    json_obj = json.loads(content)
    for obj in json_obj:
        skill_level_factors[obj['Level']] = generate_factors(obj)
    return

def generate_skill_operations(skill_obj):
    def generate_one_operation(index):
        op_fields = list(filter(lambda x : x.startswith('Operation') and x.endswith(str(index)), skill_obj.keys()))
        d = { x[len('Operation'):-1] : skill_obj[x] for x in op_fields }
        return None if len(d) == 0 else d

    max_operation = max_numbered_key(skill_obj, 'Operation')
    if max_operation is None:
        return []

    return [generate_one_operation(x) for x in range(1, max_operation+1)]

def format_skill_operation_key(operation, key, default=None):
    if not key in operation:
        return default
    value = operation[key]
    return str(value)

def dump_default_operation(operation, type):
    value_str = format_skill_operation_key(operation, 'Value')
    target_type_str = format_skill_operation_key(operation, 'TargetType', default='null target')
    value_factors_str = format_skill_operation_key(operation, 'ValueFactor')

    type = type + '({0})'.format(target_type_str)
    if value_str:
        type = type + ', values = {0}'.format(value_str)
    if value_factors_str:
        type = type + ', factors = {0}'.format(value_factors_str)
    suffix = type

    operation.pop('Value', None)
    operation.pop('TargetType', None)
    operation.pop('ValueFactor', None)
    return suffix

def dump_get_damage_r(operation, type : str):
    global skill_level_factors
    values = operation['Value']
    prefix = "physical " if "Physical" in type else "Magical "
    if len(values) == 1:
        formula = 'ATK * {0}'.format(values[0])
    else:
        v1 = float(values[0]) / 1000.0
        term1 = 'Floor[ATK * {0}]'.format(v1)

        factors = operation['ValueFactor']
        factor_value = skill_level_factors[80][int(factors[2])]
        term2 = int(values[1]) + 8 * int(float(factor_value) * float(factors[3]) / 1000.0)
        formula = term1 + ' + ' + str(term2)
    target_type = operation['TargetType']
    operation.pop('TargetType', None)
    operation.pop('Value', None)
    operation.pop('ValueFactor', None)
    return '{0}({1}), DMG = {2}'.format(type, target_type, formula)


def dump_one_skill_operation(index, operation):
    prefix = '[{0}]: '.format(index)
    suffix = '(null)'
    if not operation:
        print_line('{0}(null)'.format(prefix))
        return

    op_copy = copy.deepcopy(operation)

    type_str = format_skill_operation_key(op_copy, 'Type')
    op_copy.pop('Type', None)
    operation_handlers = {
        'GetPhysicalDamageR' : dump_get_damage_r,
        'GetMagicalDamageR' : dump_get_damage_r
        }

    if type_str:
        if type_str in operation_handlers:
            suffix = operation_handlers[type_str](op_copy, type_str)
        else:
            suffix = dump_default_operation(op_copy, type_str)
    print_line('{0}{1}'.format(prefix, suffix))

    def should_dump(op_key_value):
        k, v = op_key_value
        if k == 'ConditionType' and v == 'None':
            return False
        return True

    op_list = [op_key_value for op_key_value in op_copy.items() if should_dump(op_key_value)]
    groups_of_3 = list(zip(*(iter(op_list),) * 3))
    indent(5)
    for group in groups_of_3:
        ((k1, v1), (k2, v2), (k3, v3)) = group
        print_line('{0}={1}, {2}={3}, {4}={5}'.format(k1, str(v1), k2, str(v2), k3, str(v3)))
    indent(-5)

def format_skill_header(skill_obj):
    attr = skill_obj['AttrType']
    target_type = skill_obj['TargetType']
    components = []
    if attr != 'None':
        components.append(attr.lower())
    if 'TriggerType' in skill_obj:
        trigger = skill_obj['TriggerType']
        if trigger != 'None' and trigger != 'NextSkill':
            components.append('trigger = {0}'.format(trigger))
    if 'DurationTimeMs' in skill_obj:
        duration = skill_obj['DurationTimeMs']
        components.append('duration = {0}'.format(str(duration)))
    if 'TargetCount' in skill_obj:
        target_count = skill_obj['TargetCount']
        if target_count != 1:
            components.append('target {0} {1}'.format(target_count, target_type))
        else:
            components.append('target {0}'.format(target_type))
    else:
        components.append('target {0}'.format(target_type))
    return ', '.join(components)

def dump_one_skill(name, index=None, book_mods=None):
    global skills_by_index
    skill_obj = skills_by_index[index]
    print_line('Skill: {0} ({1})'.format(name, format_skill_header(skill_obj)))
    operations = generate_skill_operations(skill_obj)

    indent(4)
    for index, op in enumerate(operations):
        dump_one_skill_operation(index, op)

    phase = 1
    while 'NextIndex' in skill_obj:
        next_index = skill_obj['NextIndex']
        skill_obj = skills_by_index[next_index]
        print_line('-> phase {0}: {1}'.format(phase, format_skill_header(skill_obj)))
        operations = generate_skill_operations(skill_obj)

        indent(12)
        for index, op in enumerate(operations):
            dump_one_skill_operation(index, op)
        phase = phase + 1
        indent(-12)
    indent(-4)

def dump_heroes():
    global creature_by_index
    for hero in filter(lambda x : 'OpenType' in x, creature_by_index.values()):
        print_line(hero['CodeName']);
        indent(2)
        dump_one_skill('Auto Attack', index=hero['BaseSkillIndex']);
        for i in range(4):
            index_str = 'SkillIndex{0}'.format(i+1)
            book_str = 'SkillExtend{0}'.format(i+1)
            dump_one_skill("S{0}".format(i+1), index=hero[index_str], book_mods=hero[book_str])
        indent(-2)

def main():
    load_creatures_table()
    load_skills_table()
    load_skill_level_factors_table()

    dump_heroes()

try:
    args = parse_args()
    main()
except:
    print('An unknown error occurred.  Please report this bug.')
    traceback.print_exc()