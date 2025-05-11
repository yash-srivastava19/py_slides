import blessed

term = blessed.Terminal()

# Clear the terminal and move the cursor to the top-left position
print(term.home + term.clear)

# Print text at the current cursor position
print("Hello, blessed terminal!")

# Move the cursor to a specific position (row 5, column 10) and print text
print(term.move(5, 10) + "This text is at row 5, column 10.")

# Print text with color and style
print(term.color(1) + term.bold + "This text is colored and bold." + term.normal)

# You can also use f-strings for more readable formatting
text = "Formatted text"
print(f"{term.italic}{term.underline}{text}{term.normal}")