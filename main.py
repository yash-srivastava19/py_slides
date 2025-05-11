#!/usr/bin/env python3
"""
termslides: A terminal-based markdown slide presentation tool
"""
import argparse
import os
import re
import sys
from dataclasses import dataclass
from typing import List, Optional

from blessed import Terminal
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from rich.console import Console
from rich.markdown import Markdown
from rich.highlighter import JSONHighlighter


@dataclass
class Slide:
    """Represents a single slide in the presentation."""
    content: str
    notes: Optional[str] = None


class Presentation:
    """Manages a collection of slides and presentation state."""

    def __init__(self, slides: List[Slide], title: str = "Presentation"):
        self.slides = slides
        self.title = title
        self.current_slide = 0
        self.term = Terminal()
        self.console = Console()
        self.show_notes = False
        self.help_mode = False

    def next_slide(self) -> None:
        """Move to the next slide if possible."""
        if self.current_slide < len(self.slides) - 1:
            self.current_slide += 1

    def prev_slide(self) -> None:
        """Move to the previous slide if possible."""
        if self.current_slide > 0:
            self.current_slide -= 1

    def first_slide(self) -> None:
        """Move to the first slide."""
        self.current_slide = 0

    def last_slide(self) -> None:
        """Move to the last slide."""
        self.current_slide = len(self.slides) - 1

    def toggle_notes(self) -> None:
        """Toggle the display of speaker notes."""
        self.show_notes = not self.show_notes

    def toggle_help(self) -> None:
        """Toggle the help screen."""
        self.help_mode = not self.help_mode

    def _render_markdown(self, text: str) -> str:
        """Render markdown text for terminal display."""
        return Markdown(text, justify="left", style="magenta")

    

    def display_current_slide(self) -> None:
        """Display the current slide on the terminal."""
        if self.help_mode:
            self._display_help()
            return

        # Clear the terminal and set up the display area
        print(self.term.clear())
        
        # Get current slide
        slide = self.slides[self.current_slide]
        
        # Prepare the header with slide number and navigation info
        header = f"{self.title} - Slide {self.current_slide + 1}/{len(self.slides)}"
        header_x = (self.term.width - len(header)) // 2
        
        rendered_content = self._render_markdown(slide.content)
        self.console.print(rendered_content, highlight=True)
                
        # Display notes if enabled
        if self.show_notes and slide.notes:
            notes_y = self.term.height - 10
            print(self.term.move(notes_y, 0) + "-" * self.term.width)
            print(self.term.move(notes_y + 1, 2) + "Speaker Notes:")
            print(self.term.move(notes_y + 2, 4) + slide.notes)
        
        # Display footer with controls
        footer = "q:Quit | n:Next | p:Previous | h:Help | s:Toggle Notes"
        footer_y = self.term.height - 3
        print(self.term.move(footer_y - 2, 5) + self.term.bright_magenta + "Yash Srivastava 2025-05-11" + self.term.normal)
        footer_text = f"Slide {self.current_slide + 1} / {len(self.slides)}"
        print(self.term.move(footer_y - 2, self.term.width - 10 - len(footer_text)) + footer_text)
        print(self.term.move(footer_y + 1, 2) + footer)

        # print(self.term.move(footer_y, 0) + "-" * self.term.width)

    def _display_help(self) -> None:
        """Display the help screen."""
        print(self.term.clear())
        
        title = "PYSLIDES HELP"
        title_x = (self.term.width - len(title)) // 2
        print(self.term.move(2, title_x) + self.term.bold(title))
        
        help_text = """
        KEY CONTROLS:
        
        q, Ctrl+C    : Quit the presentation
        n, Right, Space : Next slide
        p, Left      : Previous slide
        f            : First slide
        l            : Last slide
        s            : Toggle speaker notes
        h            : Toggle this help screen
        
        NAVIGATION:
        
        You can navigate between slides using the arrow keys or by using
        the specific keys mentioned above.
        """
        
        # Center and display help text
        help_lines = help_text.strip().split('\n')
        start_y = (self.term.height - len(help_lines)) // 2
        
        for i, line in enumerate(help_lines):
            y_pos = start_y + i
            if y_pos < self.term.height - 2:
                print(self.term.move(y_pos, 4) + line)
        
        footer = "Press any key to return to the presentation..."
        footer_y = self.term.height - 2
        print(self.term.move(footer_y, (self.term.width - len(footer)) // 2) + footer)

    def is_last_slide(self) -> bool:
        """Check if the current slide is the last one."""
        return self.current_slide == len(self.slides) - 1

    def is_first_slide(self) -> bool:
        """Check if the current slide is the first one."""
        return self.current_slide == 0
    
    def run(self) -> None:
        """Run the presentation loop."""
        with self.term.fullscreen(), self.term.cbreak():
            while True:
                self.display_current_slide()
                
                # Get keyboard input
                key = self.term.inkey(timeout=None)
                
                # Process the key
                if key.name == 'KEY_ESCAPE' or key == 'q' or key == '\x03':  # Esc, q, or Ctrl+C
                    break
                elif self.help_mode:
                    self.help_mode = False
                
                elif self.is_last_slide() and key == 'n':
                    break
                
                elif self.is_first_slide() and key == 'p':
                    break

                elif key.name == 'KEY_RIGHT' or key == ' ' or key == 'n':
                    self.next_slide()
                elif key.name == 'KEY_LEFT' or key == 'p':
                    self.prev_slide()
                elif key == 'f':
                    self.first_slide()
                elif key == 'l':
                    self.last_slide()
                elif key == 's':
                    self.toggle_notes()
                elif key == 'h':
                    self.toggle_help()


def parse_markdown(file_path: str) -> Presentation:
    """Parse a markdown file into slides."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Use horizontal rules (---) as slide separators
    slide_separator = r'\n\s*---\s*\n'
    slide_contents = re.split(slide_separator, content)
    
    # Extract title if it exists (first H1 in the first slide)
    title_match = re.search(r'^#\s+(.+)$', slide_contents[0], re.MULTILINE)
    title = title_match.group(1) if title_match else "Presentation"
    
    slides = []
    for slide_content in slide_contents:
        # Check for speaker notes (marked with ?> prefix)
        notes_pattern = r'\?\>\s*(.*?)(?=\n\n|\Z)'
        notes_match = re.search(notes_pattern, slide_content, re.DOTALL)
        
        notes = None
        if notes_match:
            notes = notes_match.group(1).strip()
            # Remove notes from the slide content
            slide_content = re.sub(notes_pattern, '', slide_content, flags=re.DOTALL)
        
            # Add the slide
        slides.append(Slide(content=slide_content.strip(), notes=notes))
    
    return Presentation(slides, title)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Terminal-based markdown slides.')
    parser.add_argument('file', help='Markdown file to present')
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    
    presentation = parse_markdown(args.file)
    presentation.run()


if __name__ == '__main__':
    main()