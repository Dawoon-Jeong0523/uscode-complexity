'''
This module includes all functions needed to parse hierarchical structures from legal text:
- parse_high_structure
- parse_chapter_structure
- parse_section_structure
- Fixing_misparsed_context
- add_nested_matches
- parse_chapter_structure_low

These functions support Subtitle → Division → Part → Subpart → Chapter → Subchapter → Section (for titles where Parts appear under Chapters, use parse_chapter_structure_low)
as well as item-level hierarchies like (a)(1)(A)(i)...

'''
import re

def parse_high_structure(text):
    subtitle_pattern = re.compile(r"^Subtitle\s+([A-ZIVXLCDM]+)\s*—\s*(.+)$", re.IGNORECASE)
    division_pattern = re.compile(r"^Division\s+([A-ZIVXLCDM]+)\s*—\s*(.+)$", re.IGNORECASE)
    part_pattern = re.compile(r"^PART\s+([A-ZIVXLCDM]+)\s*—\s*(.+)$", re.IGNORECASE)
    subpart_pattern = re.compile(r"^Subpart\s+([A-ZIVXLCDM]+)\s*(?:—|–|-)\s*(.+)", re.IGNORECASE)
    chapter_pattern = re.compile(r"^CHAPTER\s+(\d+[a-zA-Z]?)\s*—\s*(.+)$", re.IGNORECASE)
    subchapter_pattern = re.compile(r"^SUBCHAPTER\s+([IVXLCDM]+(?:–[A-Z]+)?)\s*—\s*(.+)$", re.IGNORECASE)

    lines = text.splitlines()

    # Step 1: Determine which came first: PART or CHAPTER
    first_part_idx = first_chapter_idx = float('inf')
    for i, line in enumerate(lines):
        if part_pattern.match(line) and first_part_idx == float('inf'):
            first_part_idx = i
        if chapter_pattern.match(line) and first_chapter_idx == float('inf'):
            first_chapter_idx = i
    use_part_based_structure = first_part_idx < first_chapter_idx

    # Step 2: Initialize structure
    structure = {}
    current = {
        "subtitle": None,
        "division": None,
        "part": None,
        "subpart": None,
        "chapter": None,
        "subchapter": None,
    }

    def get_target():
        target = structure
        for level in ["subtitle", "division", "part", "subpart", "chapter", "subchapter"]:
            name = current[level]
            if name:
                target = target.setdefault(name, {})
        return target

    # Step 3: Parse based on chosen strategy
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if (m := subtitle_pattern.match(line)):
            current["subtitle"] = f"Subtitle {m[1]} — {m[2].strip()}"
            current.update(division=None, part=None, subpart=None, chapter=None, subchapter=None)
            structure.setdefault(current["subtitle"], {})

        elif (m := division_pattern.match(line)):
            current["division"] = f"Division {m[1]} — {m[2].strip()}"
            current.update(part=None, subpart=None, chapter=None, subchapter=None)
            get_target()

        elif use_part_based_structure and (m := part_pattern.match(line)):
            current["part"] = f"PART {m[1]} — {m[2].strip()}"
            current.update(subpart=None, chapter=None, subchapter=None)
            get_target()

        elif use_part_based_structure and (m := subpart_pattern.match(line)):
            current["subpart"] = f"Subpart {m[1]} — {m[2].strip()}"
            current.update(chapter=None, subchapter=None)
            get_target()

        elif (m := chapter_pattern.match(line)):
            current["chapter"] = f"CHAPTER {m[1]} — {m[2].strip()}"
            if not use_part_based_structure:
                current.update(part=None, subpart=None)
            current.update(subchapter=None)
            get_target()

        elif (m := subchapter_pattern.match(line)):
            current["subchapter"] = f"SUBCHAPTER {m[1]} — {m[2].strip()}"
            get_target()

    return structure


def parse_chapter_structure(text, allow_part=False):
    chapter_pattern = re.compile(r"^CHAPTER\s+(\d+[a-zA-Z]?)\s*—\s*(.+)$", re.IGNORECASE)
    subchapter_pattern = re.compile(r"^subchapter\s+([A-ZIVXLCDM]+)\s*—\s*(.+)$", re.IGNORECASE)
    section_pattern = re.compile(r"^§(\d+[a-zA-Z]?(–\d+)?)\s*[.]\s*(.+)$")

    structure = {}
    current = {
        "chapter": None,
        "subchapter": None,
    }

    def get_target():
        target = structure
        for level in ["chapter", "subchapter"]:
            name = current[level]
            if name:
                target = target.setdefault(name, {})
        return target

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if (m := chapter_pattern.match(line)):
            current["chapter"] = f"CHAPTER {m[1]} — {m[2].strip()}"
            current.update(subchapter=None)
            structure.setdefault(current["chapter"], {})

        elif (m := subchapter_pattern.match(line)):
            current["subchapter"] = f"SUBCHAPTER {m[1]} — {m[2].strip()}"
            get_target()

        elif (m := section_pattern.match(line)):
            section_number, section_title = m[1], m[3].strip()
            if "omitted" in section_title.lower() or "repealed" in section_title.lower():
                continue
            section_entry = f"Section. {section_number} — {section_title}"
            target = get_target()
            target.setdefault("SectionList", []).append(section_entry)

    return structure

def add_nested_matches(stripped_line, temp_result_list, indentation_level=0):
    """
    Extract nested structures like (1), (A), (i), (I) from a single line,
    and append them to temp_result_list with correct hierarchy based on order of appearance.
    No assumption about starting level: hierarchy is inferred from order.
    """
    # Combine all patterns into one list (no fixed hierarchy)
    all_patterns = [
        ('item', r'\(\s*(\d+)\s*\)'),
        ('subitem', r'\(\s*([A-Z])\s*\)'),
        ('subsubitem', r'\(\s*(i+|iv|v+|x+)\s*\)'),
        ('subsubsubitem', r'\(\s*([IVXLCDM]+)\s*\)')
    ]

    # Find all matches with type and position
    matches = []
    for level_name, pat in all_patterns:
        for m in re.finditer(pat, stripped_line):
            matches.append((m.start(), m.group(1), level_name))

    # Sort by position in the line (to keep the order)
    matches.sort()

    # Add to temp_result_list with increasing indentation
    current_indent = indentation_level
    for _, val, level_name in matches:
        temp_result_list.append((current_indent, level_name, val, stripped_line))
        current_indent += 1  # deeper level for each nested match

def parse_section_structure(text, debug=False):
    """
    Parses legal text using indentation levels and regex patterns to construct a hierarchical structure.
    """

    # Regular Expressions
    section_pattern = re.compile(r"^§(\d+[a-zA-Z–\d]*)\s*[.]\s*(.+)$")
    subsection_pattern = re.compile(r"^\(\s*([a-z])\s*\)")
    item_pattern = re.compile(r"^\(\s*(\d+)\s*\)")
    subitem_pattern = re.compile(r"^\(\s*([A-Z])\s*\)")
    subsubitem_pattern = re.compile(r"^\(\s*(i+|iv|v+|x+)\s*\)")
    subsubsubitem_pattern = re.compile(r"^\(\s*([IVXLCDM]+)\s*\)")

    # 2 - pair patterns
    subsection_item_pattern = re.compile(r"^\(\s*([a-z])\s*\)\(\s*(\d+)\s*\)")
    item_subitem_pattern = re.compile(r"^\(\s*(\d+)\s*\)\(\s*([A-Z])\s*\)")
    subitem_subsubitem_pattern = re.compile(r"^\(\s*([A-Z])\s*\)\(\s*(i+|iv|v+|x+)\s*\)")
    subsubitem_subsubsubitem_pattern = re.compile(r"^\(\s*(i+|iv|v+|x+)\s*\)\(\s*([IVXLCDM]+)\s*\)")

    # 3 - pair patterns
    subsection_item_subitem_pattern = re.compile(r"^\(\s*([a-z])\s*\)\(\s*(\d+)\s*\)\(\s*([A-Z])\s*\)")
    item_subitem_subsubitem_pattern = re.compile(r"^\(\s*(\d+)\s*\)\(\s*([A-Z])\s*\)\(\s*(i+|iv|v+|x+)\s*\)")
    subitem_subsubitem_subsubsubitem_pattern = re.compile(r"^\(\s*([A-Z])\s*\)\(\s*(i+|iv|v+|x+)\s*\)\(\s*([IVXLCDM]+)\s*\)")

    # 4 - pair patterns
    subsection_item_subitem_subsubitem_pattern = re.compile(r"^\(\s*([a-z])\s*\)\(\s*(\d+)\s*\)\(\s*([A-Z])\s*\)\(\s*(i+|iv|v+|x+)\s*\)")
    item_subitem_subsubitem_subsubsubitem_pattern = re.compile(r"^\(\s*(\d+)\s*\)\(\s*([A-Z])\s*\)\(\s*(i+|iv|v+|x+)\s*\)\(\s*([IVXLCDM]+)\s*\)")

    # Cut off pattern
    chapter_heading_pattern = re.compile(r'^\s*CHAPTER\s+\d+')
    section_heading_pattern = re.compile(r'^\s*§\d+')
    statute_break_pattern = re.compile(r'^\s*\(.*\d{4}.*Stat\..*\)$')
    pub_law_pattern = re.compile(r'^\s*Pub\. L\..*')

    # Process text line by line
    lines = text.splitlines()

    # Stack to maintain hierarchy
    stack = []
    hierarchy = {}
    temp_result_list = []

    skip_mode = False

    for line in lines:
        stripped_line = line.lstrip()
        indentation_level = len(line) - len(stripped_line)

        # 1. heading triggers skip mode
        if (
            chapter_heading_pattern.match(stripped_line.strip())
            or statute_break_pattern.match(stripped_line.strip())
            or pub_law_pattern.match(stripped_line.strip())
        ):
            stack = []
            skip_mode = True
            if debug:
                print(f"[DEBUG] Section boundary detected → skip_mode = True")
            continue

        # 2. If in skip mode, wait for next section heading
        if skip_mode:
            if section_heading_pattern.match(stripped_line):
                skip_mode = False
                if debug:
                    print(f"[DEBUG] New section detected. Exiting skip mode.")
            else:
                continue  # Skip the line entirely

        # 1️⃣ Match a section (e.g., §8432.)
        if section_match := section_pattern.match(stripped_line):
          section_number, _ = section_match.groups()

          #################################################
          section_number = section_number.lower()
          stack = [(indentation_level, section_number)]
          if section_number not in hierarchy:
              hierarchy[section_number] = {}
          if debug:
              print(f"[DEBUG] Section Detected: {section_number}, Stack: {stack}, {stripped_line}")
          temp_result_list.append((indentation_level,'section',section_number,stripped_line))
          continue

        # Remove incorrect hierarchy levels based on indentation
        while stack and stack[-1][0] >= indentation_level:
            stack.pop()

        # Find parent dictionary
        current_dict = hierarchy
        for _, key in stack:
            if key not in current_dict:
                current_dict[key] = {}
            current_dict = current_dict[key]

        # 2️⃣ Match a subsection-item pair (e.g., (a)(1))
        if subsection_item_match := subsection_item_pattern.match(stripped_line):
            subsection, item = subsection_item_match.groups()
            stack.append((indentation_level, subsection))
            stack.append((indentation_level, item))
            if subsection not in current_dict:
                current_dict[subsection] = {}
            if item not in current_dict[subsection]:
                current_dict[subsection][item] = {}
            if debug:
                print(f"[DEBUG] Subsection-Item Detected: ({subsection})({item}), Stack: {stack}, {stripped_line}")
            temp_result_list.append((indentation_level,'subsection',subsection,stripped_line))
            temp_result_list.append((indentation_level+1,'item',item,stripped_line))
            continue

        # 3️⃣ Match an item-subitem pair (e.g., (1)(A))
        if item_subitem_match := item_subitem_pattern.match(stripped_line):
            item, subitem = item_subitem_match.groups()
            stack.append((indentation_level, item))
            stack.append((indentation_level, subitem))
            if item not in current_dict:
                current_dict[item] = {}
            if subitem not in current_dict[item]:
                current_dict[item][subitem] = {}
            if debug:
                print(f"[DEBUG] Item-Subitem Detected: ({item})({subitem}), Stack: {stack}")
            temp_result_list.append((indentation_level,'item',item,stripped_line))
            temp_result_list.append((indentation_level+1,'subitem',subitem,stripped_line))
            continue

        # 4️⃣ Match a subitem-subsubitem pair (e.g., (A)(i))
        if subitem_subsubitem_match := subitem_subsubitem_pattern.match(stripped_line):
            subitem, subsubitem = subitem_subsubitem_match.groups()
            stack.append((indentation_level, subitem))
            stack.append((indentation_level, subsubitem))
            if subitem not in current_dict:
                current_dict[subitem] = {}
            if subsubitem not in current_dict[subitem]:
                current_dict[subitem][subsubitem] = {}
            if debug:
                print(f"[DEBUG] Subitem-Subsubitem Detected: ({subitem})({subsubitem}), Stack: {stack}, {stripped_line}")

            temp_result_list.append((indentation_level,'subitem',subitem,stripped_line))
            temp_result_list.append((indentation_level+1,'subsubitem',subsubitem,stripped_line))
            continue

        # 5️⃣ Match a subsubitem-subsubsubitem pair (e.g., (i)(I))
        if subsubitem_subsubsubitem_match := subsubitem_subsubsubitem_pattern.match(stripped_line):
            subsubitem, subsubsubitem = subsubitem_subsubsubitem_match.groups()
            stack.append((indentation_level, subsubitem))
            stack.append((indentation_level, subsubsubitem))
            if subsubitem not in current_dict:
                current_dict[subsubitem] = {}
            if subsubsubitem not in current_dict[subsubitem]:
                current_dict[subsubitem][subsubsubitem] = {}
            if debug:
                print(f"[DEBUG] Subsubitem-Subsubsubitem Detected: ({subsubitem})({subsubsubitem}), Stack: {stack}, {stripped_line}")

            temp_result_list.append((indentation_level,'subitem',subsubitem,stripped_line))
            temp_result_list.append((indentation_level+1,'subsubitem',subsubsubitem,stripped_line))
            continue

        # 6️⃣ Match standalone subsection (e.g., (a))
        if subsection_match := subsection_pattern.match(stripped_line):
            # If the line indicates the subsection is omitted/reserved/repealed


            if any(kw in stripped_line.lower() for kw in ['omitted', 'reserved', 'repealed']):
                continue

            subsection = subsection_match.group(1)
            stack.append((indentation_level, subsection))
            if subsection not in current_dict:
                current_dict[subsection] = {}
            if debug:
                print(f"[DEBUG] Standalone Subsection Detected: ({subsection}), Stack: {stack}, {stripped_line}")
                #print(stripped_line)

            temp_result_list.append((indentation_level,'subsection',subsection,stripped_line))
            continue

        # 7️⃣ Match standalone item (e.g., (1))
        if item_match := item_pattern.match(stripped_line):
            item = item_match.group(1)
            stack.append((indentation_level, item))
            if item not in current_dict:
                current_dict[item] = {}
            if debug:
                print(f"[DEBUG] Standalone Item Detected: ({item}), Stack: {stack}, {stripped_line}")
                #print(stripped_line)
            temp_result_list.append((indentation_level,'item',item,stripped_line))
            continue

        # 8️⃣ Match standalone subitem (e.g., (A))
        if subitem_match := subitem_pattern.match(stripped_line):
            subitem = subitem_match.group(1)
            stack.append((indentation_level, subitem))
            if subitem not in current_dict:
                current_dict[subitem] = {}
            if debug:
                print(f"[DEBUG] Standalone Subitem Detected: ({subitem}), Stack: {stack}, {stripped_line}")
            temp_result_list.append((indentation_level,'subitem',subitem,stripped_line))
            continue

        # 9️⃣ Match standalone subsubitem (e.g., (i), (ii), (iii))
        if subsubitem_match := subsubitem_pattern.match(stripped_line):
            subsubitem = subsubitem_match.group(1)
            stack.append((indentation_level, subsubitem))
            if subsubitem not in current_dict:
                current_dict[subsubitem] = {}
            if debug:
                print(f"[DEBUG] Standalone Subsubitem Detected: ({subsubitem}), Stack: {stack}, {stripped_line}")
            temp_result_list.append((indentation_level,'subsubitem',subsubitem,stripped_line))
            continue

        # 🔟 Match standalone subsubsubitem (e.g., (I), (II), (III))
        if subsubsubitem_match := subsubsubitem_pattern.match(stripped_line):
            subsubsubitem = subsubsubitem_match.group(1)
            stack.append((indentation_level, subsubsubitem))
            if subsubsubitem not in current_dict:
                current_dict[subsubsubitem] = {}
            if debug:
                print(f"[DEBUG] Standalone Subsubsubitem Detected: ({subsubsubitem}), Stack: {stack}, {stripped_line}")
            temp_result_list.append((indentation_level,'subsubsubitem',subsubsubitem,stripped_line))
            continue

        # 1️⃣ Match a subsection-item-subitem pair (e.g., (a)(1)(A))
        if subsection_item_subitem_match := subsection_item_subitem_pattern.match(stripped_line):
            subsection, item, subitem = subsection_item_subitem_match.groups()
            stack.append((indentation_level, subsection))
            stack.append((indentation_level, item))
            stack.append((indentation_level, subitem))

            if subsection not in current_dict:
                current_dict[subsection] = {}
            if item not in current_dict[subsection]:
                current_dict[subsection][item] = {}
            if subitem not in current_dict[subsection][item]:
                current_dict[subsection][item][subitem] = {}

            if debug:
                print(f"[DEBUG] Subsection-Item-Subitem Detected: ({subsection})({item})({subitem}), Stack: {stack}, {stripped_line}")

            temp_result_list.append((indentation_level,'subsection',subsection,stripped_line))
            temp_result_list.append((indentation_level+1,'item',item,stripped_line))
            temp_result_list.append((indentation_level+2,'subitem',subitem,stripped_line))

            continue

        # 2️⃣ Match an item-subitem-subsubitem pair (e.g., (1)(A)(i))
        if item_subitem_subsubitem_match := item_subitem_subsubitem_pattern.match(stripped_line):
            item, subitem, subsubitem = item_subitem_subsubitem_match.groups()
            stack.append((indentation_level,'item', item))
            stack.append((indentation_level,'subitem', subitem))
            stack.append((indentation_level,'subsubitem', subsubitem))

            if item not in current_dict:
                current_dict[item] = {}
            if subitem not in current_dict[item]:
                current_dict[item][subitem] = {}
            if subsubitem not in current_dict[item][subitem]:
                current_dict[item][subitem][subsubitem] = {}

            if debug:
                print(f"[DEBUG] Item-Subitem-Subsubitem Detected: ({item})({subitem})({subsubitem}), Stack: {stack}")

            temp_result_list.append((indentation_level,'item',item))
            temp_result_list.append((indentation_level+1,'subitem',subitem))
            temp_result_list.append((indentation_level+2,'subsubitem',subsubitem))

            continue

        # 3️⃣ Match a subitem-subsubitem-subsubsubitem pair (e.g., (A)(i)(I))
        if subitem_subsubitem_subsubsubitem_match := subitem_subsubitem_subsubsubitem_pattern.match(stripped_line):
            subitem, subsubitem, subsubsubitem = subitem_subsubitem_subsubsubitem_match.groups()
            stack.append((indentation_level,'subitem', subitem))
            stack.append((indentation_level,'subsubitem', subsubitem))
            stack.append((indentation_level,'subsubsubitem', subsubsubitem))

            if subitem not in current_dict:
                current_dict[subitem] = {}
            if subsubitem not in current_dict[subitem]:
                current_dict[subitem][subsubitem] = {}
            if subsubsubitem not in current_dict[subitem][subsubitem]:
                current_dict[subitem][subsubitem][subsubsubitem] = {}

            if debug:
                print(f"[DEBUG] Subitem-Subsubitem-Subsubsubitem Detected: ({subitem})({subsubitem})({subsubsubitem}), Stack: {stack}, {stripped_line}")

            temp_result_list.append((indentation_level,'subitem',subitem,stripped_line))
            temp_result_list.append((indentation_level+1,'subsubitem',subsubitem,stripped_line))
            temp_result_list.append((indentation_level+2,'subsubsubitem',subsubsubitem,stripped_line))

            continue

        # 4️⃣ Match a subsection-item-subitem-subsubitem pair (e.g., (a)(1)(A)(i))
        if subsection_item_subitem_subsubitem_match := subsection_item_subitem_subsubitem_pattern.match(stripped_line):
            subsection, item, subitem, subsubitem = subsection_item_subitem_subsubitem_match.groups()
            stack.append((indentation_level, subsection))
            stack.append((indentation_level, item))
            stack.append((indentation_level, subitem))
            stack.append((indentation_level, subsubitem))

            if subsection not in current_dict:
                current_dict[subsection] = {}
            if item not in current_dict[subsection]:
                current_dict[subsection][item] = {}
            if subitem not in current_dict[subsection][item]:
                current_dict[subsection][item][subitem] = {}
            if subsubitem not in current_dict[subsection][item][subitem]:
                current_dict[subsection][item][subitem][subsubitem] = {}

            if debug:
                print(f"[DEBUG] Subsection-Item-Subitem-Subsubitem Detected: ({subsection})({item})({subitem})({subsubitem}), Stack: {stack}, {stripped_line}")

            temp_result_list.append((indentation_level,'subsection',subsection,stripped_line))
            temp_result_list.append((indentation_level+1,'item',item,stripped_line))
            temp_result_list.append((indentation_level+2,'subitem',subitem,stripped_line))

            continue

        # 5️⃣ Match an item-subitem-subsubitem-subsubsubitem pair (e.g., (1)(A)(i)(I))
        if item_subitem_subsubitem_subsubsubitem_match := item_subitem_subsubitem_subsubsubitem_pattern.match(stripped_line):
            item, subitem, subsubitem, subsubsubitem = item_subitem_subsubitem_subsubsubitem_match.groups()
            stack.append((indentation_level,'item', item))
            stack.append((indentation_level,'subitem', subitem))
            stack.append((indentation_level,'subsubitem', subsubitem))
            stack.append((indentation_level,'subsubsubitem', subsubsubitem))

            if item not in current_dict:
                current_dict[item] = {}
            if subitem not in current_dict[item]:
                current_dict[item][subitem] = {}
            if subsubitem not in current_dict[item][subitem]:
                current_dict[item][subitem][subsubitem] = {}
            if subsubsubitem not in current_dict[item][subitem][subsubitem]:
                current_dict[item][subitem][subsubitem][subsubsubitem] = {}

            if debug:
                print(f"[DEBUG] Item-Subitem-Subsubitem-Subsubsubitem Detected: ({item})({subitem})({subsubitem})({subsubsubitem}), Stack: {stack}, {stripped_line}")

            temp_result_list.append((indentation_level,'item',item,stripped_line))
            temp_result_list.append((indentation_level+1,'subitem',subitem,stripped_line))
            temp_result_list.append((indentation_level+2,'subsubitem',subsubitem,stripped_line))

            continue

        # 🚨 NEW: If no pattern matched but nested structures exist, handle them
        if re.search(r'\(\s*(\d+|[A-Z]|i+|iv|v+|x+|[IVXLCDM]+)\s*\)', stripped_line):
            if debug:
                print(f"[DEBUG] Nested structures found in line: {stripped_line}")
            add_nested_matches(stripped_line, temp_result_list, indentation_level)

    return temp_result_list

def Fixing_misparsed_context(parsed_list):
    """
    Fix misparsed roman numerals and remove duplicate entries **only between adjacent rows**.
    Additionally, if the same (type, value) appears again **within the same subsection**, add 'dup' to its value.
    """
    corrected = parsed_list.copy()

    # Define the priority of levels (lower number means higher priority)
    level_priority = {
        'section': 0,
        'subsection': 1,
        'item': 2,
        'subitem': 3,
        'subsubitem': 4,
        'subsubsubitem': 5
    }

    # === Step 1: fix misparsed roman numerals (same as before) ===
    i = 1
    while i < len(corrected):
        curr_indent, curr_type, curr_value, curr_text = corrected[i]
        prev_indent, prev_type, prev_value, prev_text = corrected[i - 1]

        curr_value_lower = curr_value.lower()
        prev_value_lower = prev_value.lower()

        # Case 1: Fix misparsed roman numerals
        if curr_type == 'subsubitem' and re.fullmatch(r'(ii|iii|iv|v+|x+)', curr_value_lower):
            if prev_type == 'subsection' and re.fullmatch(r'(i+|iv|v+|x+)', prev_value_lower):
                corrected[i - 1] = (prev_indent, 'subsubitem', prev_value, prev_text)

        elif curr_type == 'subsubsubitem' and re.fullmatch(r'(ii|iii|iv|v+|x+)', curr_value_lower):
            if prev_type in ['subitem', 'subsubitem'] and re.fullmatch(r'(i+|iv|v+|x+)', prev_value_lower):
                corrected[i - 1] = (prev_indent, 'subsubsubitem', prev_value, prev_text)

        elif curr_type == 'subitem' and re.fullmatch(r'(v|x|i+)', curr_value_lower):
            if prev_type == 'subsubsubitem' and re.fullmatch(r'(i+|iv|v+|x+)', prev_value_lower):
                corrected[i] = (curr_indent, 'subsubsubitem', curr_value, curr_text)

        # === ✅ check only with the previous row for adjacent duplicates ===
        if (curr_text.strip() == prev_text.strip()) and (curr_value.strip() == prev_value.strip()):
            prev_priority = level_priority.get(prev_type, 99)
            curr_priority = level_priority.get(curr_type, 99)

            if curr_priority < prev_priority:
                del corrected[i - 1]
            else:
                del corrected[i]
            continue  # don't increment i if deleted

        i += 1

    return corrected

def parse_chapter_structure_low(text):
    chapter_pattern = re.compile(r"^CHAPTER\s+(\d+[a-zA-Z]?)\s*—\s*(.+)$", re.IGNORECASE)
    subchapter_pattern = re.compile(r"^SUBCHAPTER\s+([A-ZIVXLCDM]+(?:–[A-Z]+)?)\s*—\s*(.+)$", re.IGNORECASE)
    part_pattern = re.compile(r"^PART\s+([A-ZIVXLCDM]+)\s*—\s*(.+)$", re.IGNORECASE)
    subpart_pattern = re.compile(r"^Subpart\s+([A-ZIVXLCDM]+)\s*(?:—|–|-)\s*(.+)$", re.IGNORECASE)
    section_pattern = re.compile(r"^§(\d+[a-zA-Z]?(–\d+)?)\s*[.]\s*(.+)$")

    structure = {}
    current = {
        "chapter": None,
        "subchapter": None,
        "part": None,
        "subpart": None,
    }

    def get_target():
        target = structure
        for level in ["chapter", "subchapter", "part", "subpart"]:
            name = current[level]
            if name:
                target = target.setdefault(name, {})
        return target

    # Track whether we are inside a chapter/subchapter block
    in_valid_block = False

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if (m := chapter_pattern.match(line)):
            current["chapter"] = f"CHAPTER {m[1]} — {m[2].strip()}"
            current.update(subchapter=None, part=None, subpart=None)
            structure.setdefault(current["chapter"], {})
            in_valid_block = True
            continue

        elif (m := subchapter_pattern.match(line)):
            current["subchapter"] = f"SUBCHAPTER {m[1]} — {m[2].strip()}"
            current.update(part=None, subpart=None)
            get_target()
            in_valid_block = True
            continue

        elif allow_part and in_valid_block and (m := part_pattern.match(line)):
            current["part"] = f"PART {m[1]} — {m[2].strip()}"
            current.update(subpart=None)
            get_target()
            continue

        elif allow_part and in_valid_block and (m := subpart_pattern.match(line)):
            current["subpart"] = f"Subpart {m[1]} — {m[2].strip()}"
            get_target()
            continue

        elif (m := section_pattern.match(line)):
            section_number, section_title = m[1], m[3].strip()
            if "omitted" in section_title.lower() or "repealed" in section_title.lower():
                continue
            section_entry = f"Section. {section_number} — {section_title}"
            target = get_target()
            target.setdefault("SectionList", []).append(section_entry)

    return structure


