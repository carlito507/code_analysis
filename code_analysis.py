import ast
import sys
import os
from typing import List, Union, Set
from colorama import Fore, Style, init
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

init(autoreset=True)

class CodeStructureAnalyzer(ast.NodeVisitor):
    """
    A custom AST node visitor class to analyze the structure of Python code.

    This class identifies functions, classes, and imported modules in the given
    Python code using the Abstract Syntax Tree (AST) representation. It also
    extracts docstrings from functions and classes and analyzes dependencies.
    """

    def __init__(self) -> None:
        super().__init__()
        self.functions: Dict[str, Union[str, None]] = {}
        self.classes: Dict[str, Union[str, None]] = {}
        self.dependencies: Set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Visit a function definition node in the AST.

        :param node: The FunctionDef node to visit.
        """
        print(f"{Fore.GREEN}Function: {node.name}")
        docstring = ast.get_docstring(node)
        if docstring:
            print(f"\tDocstring: {docstring}")
        self.functions[node.name] = ast.get_docstring(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visit a class definition node in the AST.

        :param node: The ClassDef node to visit.
        """
        print(f"{Fore.BLUE}Class: {node.name}")
        docstring = ast.get_docstring(node)
        if docstring:
            print(f"\tDocstring: {docstring}")
        self.classes[node.name] = ast.get_docstring(node)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """
        Visit an import statement node in the AST.

        :param node: The Import node to visit.
        """
        for alias in node.names:
            print(f"{Fore.YELLOW}Import: {alias.name}")
            self.dependencies.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Visit an import-from statement node in the AST.

        :param node: The ImportFrom node to visit.
        """
        for alias in node.names:
            print(f"{Fore.YELLOW}Import: {node.module}.{alias.name}")
            self.dependencies.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)


def analyze_file(file_path: str) -> None:
    """
    Analyze the given Python file using the CodeStructureAnalyzer.

    :param file_path: The path to the Python file to analyze.
    """
    with open(file_path, "r") as file:
        code = file.read()

    tree = ast.parse(code)
    analyzer = CodeStructureAnalyzer()
    analyzer.visit(tree)
    print(f"\n{Fore.RED}Dependencies:")
    for dependency in analyzer.dependencies:
        print(f"\t{dependency}")
    generate_pdf_report(analyzer, file_path)


def generate_pdf_report(analyzer: CodeStructureAnalyzer, file_path: str) -> None:
    """
    Generate a stylized PDF report of the code analysis.

    :param analyzer: The CodeStructureAnalyzer instance that contains the analysis.
    :param file_path: The path to the Python file analyzed.
    """
    output_file = os.path.splitext(file_path)[0] + "_analysis_report.pdf"
    doc = SimpleDocTemplate(output_file, pagesize=landscape(letter))
    report_elements = []

    # Title
    title = f"Code Analysis Report: {os.path.basename(file_path)}"
    report_elements.append(Paragraph(title, get_title_style()))

    # Function, Class, and Import Table
    data = [['Type', 'Name', 'Docstring']]
    for function in analyzer.functions:
        data.append(['Function', function, analyzer.functions[function]])
    for class_name in analyzer.classes:
        data.append(['Class', class_name, analyzer.classes[class_name]])
    for imported_module in analyzer.dependencies:
        data.append(['Import', imported_module, ''])

    table = Table(data)
    table.setStyle(get_table_style())
    report_elements.append(table)

    # Write the PDF
    doc.build(report_elements)

def get_title_style():
    # Define the style for the title of the report
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle

    return ParagraphStyle(
        name='Title',
        fontSize=18,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

def get_table_style():
    # Define the style for the table in the report
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_python_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    analyze_file(file_path)
