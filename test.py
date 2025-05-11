from rich.console import Console
from rich.markdown import Markdown
from rich.highlighter import RegexHighlighter
from rich.theme import Theme
from rich.text import Text
from rich import box
from rich.panel import Panel
from rich.columns import Columns

class HeadingHighlighter(RegexHighlighter):
    """Custom highlighter for markdown headings to match the style in the image."""
    
    base_style = "markdown."
    highlights = [
        # Match h1 headings (# Heading)
        r"(?P<h1>^# .*$)",
        # Match h2 headings (## Heading)
        r"(?P<h2>^## .*$)",
        # Match h3 headings (### Heading)
        r"(?P<h3>^### .*$)",
        # Match code blocks
        r"(?P<code>`.*?`)",
    ]

class CustomMarkdownRenderer:
    """Custom renderer for markdown content with special heading styling."""
    
    def __init__(self):
        # Define custom theme for different heading levels
        self.theme = Theme({
            "markdown.h1": "bold bright_cyan",
            "markdown.h2": "bold bright_white",
            "markdown.h3": "bold yellow",
            "markdown.code": "bright_green",
            "slide.title": "bright_cyan",
            "slide.footer_left": "bright_magenta", 
            "slide.footer_right": "white",
            "code.keyword": "pink3",
            "code.function": "cyan",
            "code.string": "bright_green",
            "code.comment": "bright_black",
            "code.package": "pink3",
            "code.import": "pink3"
        })
        
        self.console = Console(theme=self.theme, highlight=False)
        self.highlighter = HeadingHighlighter()
    
    def render_heading(self, text, level):
        """Render a heading based on its level."""
        # Remove the heading markers (# symbols)
        content = text.strip()
        if level == 1:
            # Extract the actual heading text (remove the # prefix)
            heading_text = content[2:].strip()
            # Create a panel with the heading, preceded by a colored block (■)
            return Text("■ ", style="slide.title") + Text(heading_text, style="slide.title")
        elif level == 2:
            heading_text = content[3:].strip()
            return Text(heading_text, style="markdown.h2")
        elif level == 3:
            heading_text = content[4:].strip()
            return Text(heading_text, style="markdown.h3")
        return Text(content, style=f"markdown.h{level}")
    
    def render_code_block(self, code, language=None):
        """Render a code block with syntax highlighting."""
        # Simple syntax highlighting
        highlighted_code = code
        
        # Apply basic syntax highlighting for keywords
        keywords = ["package", "import", "func", "def", "class", "return", "if", "else", "for", "while"]
        for keyword in keywords:
            highlighted_code = highlighted_code.replace(f"{keyword} ", f"[code.keyword]{keyword}[/] ")
        
        # Handle string literals
        parts = []
        in_string = False
        current = ""
        
        for char in highlighted_code:
            if char == '"' and not in_string:
                parts.append(current)
                current = '"'
                in_string = True
            elif char == '"' and in_string:
                current += '"'
                parts.append(f"[code.string]{current}[/]")
                current = ""
                in_string = False
            else:
                current += char
        
        parts.append(current)
        highlighted_code = "".join(parts)
        
        return Panel(Text.from_markup(highlighted_code), border_style="dim", padding=(1, 2))
    
    def render_slide(self, markdown_content, footer_left=None, footer_right=None):
        """Render a complete slide with the given markdown content and footer."""
        # Clear the console
        self.console.clear()
        
        # Split content into lines
        lines = markdown_content.strip().split("\n")
        
        for i, line in enumerate(lines):
            if line.startswith("# "):
                # Render h1 heading (title)
                self.console.print(self.render_heading(line, 1), style="slide.title")
                self.console.print()  # Empty line after title
            elif line.startswith("## "):
                # Render h2 heading
                self.console.print(self.render_heading(line, 2))
                self.console.print()
            elif line.startswith("### "):
                # Render h3 heading
                self.console.print(self.render_heading(line, 3))
                self.console.print()
            elif line.startswith("```") and i+1 < len(lines):
                # Handle code blocks
                code_block = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_block.append(lines[i])
                    i += 1
                
                # Render the code block
                self.console.print(self.render_code_block("\n".join(code_block)))
            else:
                # Regular text
                self.console.print(line)
        
        # Add spacing before footer
        self.console.print("\n\n")
        
        # Render footer
        if footer_left or footer_right:
            columns = []
            if footer_left:
                columns.append(Text(footer_left, style="slide.footer_left"))
            else:
                columns.append(Text(""))
                
            if footer_right:
                columns.append(Text(footer_right, style="slide.footer_right"))
            
            self.console.print(Columns(columns, equal=True, expand=True))

# Example usage
if __name__ == "__main__":
    renderer = CustomMarkdownRenderer()
    
    slide_content = """
# Welcome to Slides

## A terminal based presentation tool

### Example Code

```
package main

import "fmt"

func main() {
    fmt.Println("Written in Go!")
}
```
"""
    
    renderer.render_slide(
        slide_content,
        footer_left="Maas Lalani 2021-06-19", 
        footer_right="Slide 1 / 7"
    )