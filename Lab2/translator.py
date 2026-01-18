class CppToPython:
    def __init__(self):
        self.tabs = 0
        self.block = ''
        self.current_block = []
        self.in_function = False
        self.function_name = ""
        self.python_lines = []

    def translate(self, cpp_file):
        self.python_lines = []
        temp_to_write = ""

        for line in cpp_file:
            line = line.strip()
            if not line:
                continue

            if "}" == line:
                if self.tabs > 0:
                    self.tabs -= 1
                if self.in_function and self.function_name:
                    self.in_function = False
                    self.function_name = ""
                continue

            if line == "{":
                self.tabs += 1
                continue

            if "using" in line or "#include" in line:
                continue

            indent = "    " * self.tabs

            if line == "break;" or line == "break":
                self.add_line(f"{indent}break")
                continue

            if "for" in line and not "=" in line.split("for")[0]:
                self.translate_for(line, indent)
                self.tabs += 1
                continue

            elif "else" in line and "if" in line:
                self.tabs -= 1
                indent = "    " * self.tabs
                self.translate_else_if(line, indent)
                self.tabs += 1
                continue

            elif "else" in line and "if" not in line:
                self.tabs -= 1
                indent = "    " * self.tabs
                self.translate_else(line, indent)
                self.tabs += 1
                continue

            elif "if" in line and "else" not in line:
                self.translate_if(line, indent)
                self.tabs += 1
                continue

            elif self.is_function_declaration(line):
                self.translate_function(line, indent)
                self.tabs += 1
                continue

            elif "cout" in line and temp_to_write == "":
                temp_to_write = self.translate_cout(line, temp_to_write, indent)

            elif "<<" in line and temp_to_write != "":
                temp_to_write = self.translate_cout_continuation(line, temp_to_write, indent)

            elif self.is_variable_declaration(line) and temp_to_write == "":
                self.translate_variables(line, indent)

            elif ("++" in line or "--" in line) and "=" not in line and ";" in line:
                self.translate_increment(line, indent)

            elif "=" in line and ";" in line and "==" not in line:
                self.translate_assignment(line, indent)

            elif "(" in line and ")" in line and line.endswith(";") and not any(
                    keyword in line for keyword in ["if", "for", "while"]):
                self.translate_function_call(line, indent)

            elif "return" in line:
                self.translate_return(line, indent)

        return self.python_lines

    def add_line(self, line):
        self.python_lines.append(line)

    def is_function_declaration(self, line):
        types = ["void", "int", "float", "double", "string", "bool", "char"]
        if not line or "(" not in line or ")" not in line:
            return False
        if line.endswith(";"):
            return False
        first_word = line.split()[0] if line.split() else ""
        return first_word in types

    def is_variable_declaration(self, line):
        types = ["string", "int", "float", "double", "bool", "char"]
        first_word = line.split()[0] if line.split() else ""
        return first_word in types and "(" not in line

    def translate_variables(self, line, indent):
        types = ["string", "int", "float", "double", "bool", "char", ";", "const"]
        line = line.replace(";", "").strip()

        if "[" in line and "]" in line:
            for t in types:
                line = line.replace(t, "")
            line = line.strip()

            var_name = line.split("[")[0].strip()
            size_part = line.split("[")[1].split("]")[0].strip()

            if "=" in line and "{" in line:
                self.add_line(f"{indent}{var_name} = [0] * {size_part}")
            else:
                self.add_line(f"{indent}{var_name} = [0] * {size_part}")
            return

        if "," in line:
            for type_name in types:
                line = line.replace(type_name, "")
            variables = line.split(",")
            for var in variables:
                if "=" in var:
                    var_name, var_value = var.split("=")
                    var_name = var_name.strip()
                    var_value = var_value.strip()
                    var_value = var_value.replace("true", "True").replace("false", "False")
                    self.add_line(f"{indent}{var_name} = {var_value}")
                else:
                    var_name = var.strip()
                    if var_name:
                        self.add_line(f"{indent}{var_name} = 0")
        else:
            for type_name in types:
                line = line.replace(type_name, "")
            line = line.strip()
            line = line.replace("true", "True").replace("false", "False")
            if "=" not in line and line:
                self.add_line(f"{indent}{line} = 0")
            elif line:
                self.add_line(f"{indent}{line}")

    def translate_increment(self, line, indent):
        line = line.replace(";", "").strip()

        if "[" in line and "]" in line:
            if "++" in line:
                base = line.replace("++", "").strip()
                var_name = base.split("[")[0].strip()
                index_part = base.split("[")[1].split("]")[0].strip()
                index_part = self.convert_char_index(index_part)
                self.add_line(f"{indent}{var_name}[{index_part}] += 1")
            elif "--" in line:
                base = line.replace("--", "").strip()
                var_name = base.split("[")[0].strip()
                index_part = base.split("[")[1].split("]")[0].strip()
                index_part = self.convert_char_index(index_part)
                self.add_line(f"{indent}{var_name}[{index_part}] -= 1")
        else:
            if "++" in line:
                var = line.replace("++", "").strip()
                self.add_line(f"{indent}{var} += 1")
            elif "--" in line:
                var = line.replace("--", "").strip()
                self.add_line(f"{indent}{var} -= 1")

    def translate_assignment(self, line, indent):
        line = line.replace(";", "").strip()

        types = ["int", "float", "double", "bool", "char"]
        for t in types:
            if line.startswith(t + " "):
                line = line[len(t):].strip()
                break

        if any(op in line for op in ["+=", "-=", "*=", "/=", "%="]):
            self.add_line(f"{indent}{line}")
            return

        if "=" not in line:
            self.add_line(f"{indent}{line}")
            return

        parts = line.split("=", 1)
        lhs = parts[0].strip()
        rhs = parts[1].strip()

        if "'" in rhs and any(op in rhs for op in ['+', '-']):
            rhs = self.convert_char_expression(rhs)

        rhs = rhs.replace("true", "True").replace("false", "False")

        if "[" in lhs and "]" in lhs:
            var_name = lhs.split("[")[0].strip()
            index_part = lhs.split("[")[1].split("]")[0].strip()
            index_part = self.convert_char_index(index_part)
            lhs = f"{var_name}[{index_part}]"

        self.add_line(f"{indent}{lhs} = {rhs}")

    def convert_char_index(self, index):
        index = index.strip()

        if " - '" in index:
            parts = index.split(" - '", 1)
            var_part = parts[0].strip()
            rest = parts[1]
            if "'" in rest:
                char_part = rest.split("'", 1)[0]
                if len(var_part) == 1 and var_part.isalpha():
                    return f"ord({var_part}) - ord('{char_part}')"
                return f"{var_part} - ord('{char_part}')"

        if "'a'" in index or "'A'" in index:
            result = index
            i = 0
            while i < len(result):
                if result[i] == "'" and i + 2 < len(result) and result[i+2] == "'":
                    char = result[i+1]
                    replacement = f"ord('{char}')"
                    result = result[:i] + replacement + result[i+3:]
                    i += len(replacement)
                else:
                    i += 1
            return result

        return index

    def convert_char_expression(self, expr):
        expr = expr.strip()
        if "(char)" in expr:
            expr = expr.replace("(char)", "").strip()
        if expr.startswith("(") and expr.endswith(")"):
            expr = expr[1:-1].strip()

        if "'a' +" in expr or "'a'+" in expr:
            if "'a' +" in expr:
                parts = expr.split("'a' +", 1)
            else:
                parts = expr.split("'a'+", 1)
            var_part = parts[1].strip()
            return f"chr(ord('a') + {var_part})"

        if "'A' +" in expr or "'A'+" in expr:
            if "'A' +" in expr:
                parts = expr.split("'A' +", 1)
            else:
                parts = expr.split("'A'+", 1)
            var_part = parts[1].strip()
            return f"chr(ord('A') + {var_part})"

        if " + '0'" in expr or "+'0'" in expr:
            if " + '0'" in expr:
                parts = expr.split(" + '0'", 1)
            else:
                parts = expr.split("+'0'", 1)
            var_part = parts[0].strip()
            return f"chr(ord('0') + {var_part})"

        return f"chr({expr})"

    def translate_cout(self, line, temp_to_write, indent):
        line = line.replace("endl", "").strip()
        parts = [part.strip() for part in line.split("<<") if "cout" not in part and part.strip()]

        processed_parts = []
        for part in parts:
            processed_parts.append(self.process_cout_part(part))

        to_write = f"{indent}print("
        to_write += ", ".join(processed_parts)

        if ";" in line:
            to_write = to_write.replace(";", "")
            to_write = to_write.rstrip(", ")
            to_write += ")"
            self.add_line(to_write)
            return ""
        else:
            return to_write

    def translate_cout_continuation(self, line, temp_to_write, indent):
        line = line.replace("endl", "").strip()
        parts = [part.strip() for part in line.split("<<") if part.strip()]

        processed_parts = []
        for part in parts:
            processed_parts.append(self.process_cout_part(part))

        to_write = temp_to_write
        if processed_parts:
            to_write += ", " + ", ".join(processed_parts)

        if ";" in line:
            to_write = to_write.replace(";", "")
            to_write = to_write.rstrip(", ")
            to_write += ")"
            self.add_line(to_write)
            return ""
        else:
            return to_write

    def process_cout_part(self, part):
        part = part.strip()
        if not part or part == "endl":
            return ""

        if "(char)" in part:
            inner = part.replace("(char)", "").strip()
            inner = inner.strip("()")

            if "'a' +" in inner or "'a'+" in inner:
                if "'a' +" in inner:
                    var_part = inner.split("'a' +")[1].strip()
                else:
                    var_part = inner.split("'a'+")[1].strip()
                return f"chr(ord('a') + {var_part})"

            if "'A' +" in inner or "'A'+" in inner:
                if "'A' +" in inner:
                    var_part = inner.split("'A' +")[1].strip()
                else:
                    var_part = inner.split("'A'+")[1].strip()
                return f"chr(ord('A') + {var_part})"

            return part

        return part

    def translate_for(self, line, indent):
        line = line.replace("{", "").strip()
        start = line.find("(")
        end = line.rfind(")")
        if start != -1 and end != -1:
            content = line[start + 1:end]
        else:
            content = line.replace("for", "").strip()

        parts = [part.strip() for part in content.split(";")]

        if len(parts) != 3:
            self.add_line(f"{indent}# UNHANDLED FOR: {line}")
            return

        init, condition, increment = parts

        for type_name in ["int", "float", "double"]:
            init = init.replace(type_name, "").strip()

        if "=" in init:
            var_name = init.split("=")[0].strip()
            start_value = init.split("=")[1].strip()
        else:
            var_name = init
            start_value = "0"

        if "*" in condition and "<=" in condition:
            limit_var = condition.split("<=")[1].strip()
            self.add_line(f"{indent}for {var_name} in range({start_value}, int({limit_var} ** 0.5) + 1):")
            return

        if "<=" in condition:
            var, limit = condition.split("<=")
            limit = limit.strip()
            self.add_line(f"{indent}for {var_name} in range({start_value}, {limit} + 1):")
        elif ">=" in condition:
            var, limit = condition.split(">=")
            limit = limit.strip()
            self.add_line(f"{indent}for {var_name} in range({start_value}, {limit} - 1, -1):")
        elif "<" in condition:
            var, limit = condition.split("<")
            limit = limit.strip()
            self.add_line(f"{indent}for {var_name} in range({start_value}, {limit}):")
        elif ">" in condition:
            var, limit = condition.split(">")
            limit = limit.strip()
            self.add_line(f"{indent}for {var_name} in range({start_value}, {limit}, -1):")

    def translate_else_if(self, line, indent):
        line = line.replace("{", "").replace("}", "").strip()

        start = line.find("(")
        end = line.rfind(")")
        if start != -1 and end != -1:
            condition = line[start + 1:end]
        else:
            condition = line.replace("else if", "").strip()

        condition = self.translate_condition(condition)
        self.add_line(f"{indent}elif {condition}:")

    def translate_else(self, line, indent):
        self.add_line(f"{indent}else:")

    def translate_if(self, line, indent):
        line = line.replace("{", "").strip()

        start = line.find("(")
        end = line.rfind(")")
        if start != -1 and end != -1:
            condition = line[start + 1:end]
        else:
            condition = line.replace("if", "").strip()

        condition = self.translate_condition(condition)
        self.add_line(f"{indent}if {condition}:")

    def translate_condition(self, condition):
        condition = condition.replace("&&", " and ").replace("||", " or ")
        condition = condition.replace("!", " not ")
        condition = condition.replace("true", "True").replace("false", "False")

        condition = " ".join(condition.split())

        return condition

    def translate_function(self, line, indent):
        return_types = ["void", "int", "float", "double", "string", "bool", "char"]
        function_line = line

        for return_type in return_types:
            if function_line.startswith(return_type):
                function_line = function_line.replace(return_type, "", 1).strip()
                break

        function_line = function_line.replace("{", "").strip()

        if "(" in function_line and ")" in function_line:
            func_name = function_line.split("(")[0].strip()
            params_part = function_line.split("(")[1].split(")")[0]

            params = []
            if params_part.strip():
                param_list = params_part.split(",")
                for param in param_list:
                    param = param.strip()
                    for param_type in return_types + ["const", "&"]:
                        param = param.replace(param_type, "").strip()
                    param = param.replace("[", "").replace("]", "")
                    param_name = param.split()[-1] if param.split() else param
                    param_name = param_name.strip()
                    if param_name:
                        params.append(param_name)

            self.in_function = True
            self.function_name = func_name
            self.add_line(f"{indent}def {func_name}({', '.join(params)}):")

    def translate_function_call(self, line, indent):
        line = line.replace(";", "").strip()
        self.add_line(f"{indent}{line}")

    def translate_return(self, line, indent):
        line = line.replace(";", "").strip()
        return_value = line.replace("return", "").strip()

        if return_value:
            self.add_line(f"{indent}return {return_value}")
        else:
            self.add_line(f"{indent}return")

    def save_to_file(self, output_filename):
        with open(output_filename, "w") as f:
            f.write('\n'.join(self.python_lines))
            f.write('\n')


def main():
    translator = CppToPython()

    with open("input1.cpp", "r") as cpp_file:
        translator.translate(cpp_file)
    translator.save_to_file("input1.py")
    print("Translated: input1.cpp → input1.py")

    translator2 = CppToPython()
    with open("input2.cpp", "r") as cpp_file:
        translator2.translate(cpp_file)
    translator2.save_to_file("input2.py")
    print("Translated: input2.cpp → input2.py")


if __name__ == "__main__":
    main()